from django.core.exceptions import ValidationError

from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes

from rest_framework.fields import set_value

from rest_framework.utils import model_meta
from rest_framework.compat import OrderedDict
from pdb import set_trace
import functools
import copy

class BaseProxyRelationalField(serializers.Field):
    relation_field = None
    relation_field_name = 'ids'

    parent_instance = None

    def bind(self, field_name, parent):
        self.relation_field.bind(field_name, parent)
        return super(BaseProxyRelationalField, self).bind(field_name, parent)

    def __init__(self, **kwargs):
        self.relation_field = kwargs.pop('relation_field')
        super(BaseProxyRelationalField, self).__init__(**kwargs)

    def to_representation(self, obj):
        return {
            self.relation_field_name: self.render_result(obj)
        }

    def get_attribute(self, instance):
        self.parent_instance = instance
        return self.relation_field.get_attribute(instance)

    def to_internal_value(self, data):
        value = data[self.relation_field_name]
        return self.relation_field.to_internal_value(value)

    def render_result(self, obj):
        return self.relation_field.to_representation(obj)


class HyperlinkedProxyRelationalField(BaseProxyRelationalField):
    def to_representation(self, obj):
        request = self.context.get('request', None)
        format = self.context.get('format', None)

        return {
            "links": self.build_links(obj, request, format),
            "ids": self.render_result(obj)
        }

    def build_links(self, obj, request, format):
        return 'please implement'


def getFromDict(dataDict, mapList):
    return functools.reduce(lambda d, k: d[k], mapList, dataDict)

def setInDict(dataDict, mapList, value):
    getFromDict(dataDict, mapList[:-1])[mapList[-1]] = value

class SubclassedDictionary(dict):
    rendered_dict = None

    def __init__(self, new_dict, condition=None, *args, **kwargs):
        super(SubclassedDictionary, self).__init__(new_dict, *args, **kwargs)
        self.paths = []
        self.get_paths(condition)

    def _get_paths_recursive(self, condition, iterable, parent_path=[]):
        path = []
        for key, value in iterable.items():
            # If we find an iterable, recursively obtain new paths.
            if isinstance(value, (dict, list, set, tuple)):
                # Make sure to remember where we have been (parent_path + [key])
                recursed_path = self._get_paths_recursive(condition, value, parent_path + [key])
                if recursed_path:
                    self.paths.append(parent_path + recursed_path)
            elif condition(value) is True:
                self.paths.append(parent_path + [key])

    def get_paths(self, condition=None):
        # Condition MUST be a function that returns a bool!
        self.paths = []
        if condition is not None:
            return self._get_paths_recursive(condition, self)

        

class GroupedSerializer(serializers.Serializer):
    composition = None
    field_locations = []

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    def to_representation(self, instance):
        self.current_instance = instance

        self.set_composition()
        ret = self.composition

        for path in ret.paths:
            result = getFromDict(ret, path)
            setInDict(ret, path, result(self.current_instance))

        return ret

    def set_composition(self):

        def bound_functions(value):
            try:
                return value.__dict__['type'] == "field_group"
            except ValueError:
                return False

        self.composition = SubclassedDictionary({
             self.create_field_group(['id']),
            "attributes":self.create_field_group(['name'])
        }, bound_functions)



    def compose(self):

        return self.composition.render()

    def create_field(self, field):
        pass

    def create_field_group(self, fields):
        func = functools.partial(
            self.build_field_dictionary,
            fields)
        func.__dict__['type'] = "field_group"
        func.__dict__['fields'] = fields
        return func

    def field_to_internal_value(self, field, data):
        ret = OrderedDict()
        errors = OrderedDict()

        validate_method = getattr(
            self,
            'validate_' +
            field.field_name,
            None)
        primitive_value = field.get_value(data)
        try:
            validated_value = field.run_validation(primitive_value)
            if validate_method is not None:
                validated_value = validate_method(validated_value)
        except ValidationError as exc:
            errors[field.field_name] = exc.detail
        except DjangoValidationError as exc:
            errors[field.field_name] = list(exc.messages)
        except SkipField:
            pass
        else:
            set_value(ret, field.source_attrs, validated_value)

        if errors:
            raise ValidationError(errors)

        return ret

    def to_internal_value(self, data):
        """
        Dict of native values <- Dict of primitive datatypes.
        """
        self.set_composition()
        
        return_dict = dict()
        paths = self.composition.paths

        for path in paths:
            try:
                data_group = getFromDict(data, path)
            except KeyError:
                continue
            
            group_fields = data_group.keys()
            
            fields = [
                field for field in self.fields.values() 
                if field.field_name in group_fields
            ]


            for field in fields:
                return_dict.update(self.field_to_internal_value(field, data_group))
            

        return return_dict

    def build_field_dictionary(self, field_array, instance):
        ret = OrderedDict()
        fields = [
            field
            for field in self.fields.values
            () if field.field_name in field_array]
        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            if attribute is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret


    def create(self, validated_data):
        """
        We have a bit of extra checking around this in order to provide
        descriptive messages when something goes wrong, but this method is
        essentially just:

            return ExampleModel.objects.create(**validated_data)

        If there are many to many fields present on the instance then they
        cannot be set until the model is instantiated, in which case the
        implementation is like so:

            example_relationship = validated_data.pop('example_relationship')
            instance = ExampleModel.objects.create(**validated_data)
            instance.example_relationship = example_relationship
            return instance

        The default implementation also does not handle nested relationships.
        If you want to support writable nested relationships you'll need
        to write an explicit `.create()` method.
        """
        raise_errors_on_nested_writes('create', self, validated_data)

        ModelClass = self.Meta.model

        # Remove many-to-many relationships from validated_data.
        # They are not valid arguments to the default `.create()` method,
        # as they require that the instance has already been saved.
        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        try:
            instance = ModelClass.objects.create(**validated_data)
        except TypeError as exc:
            msg = (
                'Got a `TypeError` when calling `%s.objects.create()`. '
                'This may be because you have a writable field on the '
                'serializer class that is not a valid argument to '
                '`%s.objects.create()`. You may need to make the field '
                'read-only, or override the %s.create() method to handle '
                'this correctly.\nOriginal exception text was: %s.' %
                (
                    ModelClass.__name__,
                    ModelClass.__name__,
                    self.__class__.__name__,
                    exc
                )
            )
            raise TypeError(msg)

        # Save many-to-many relationships after the instance is created.
        if many_to_many:
            for field_name, value in many_to_many.items():
                setattr(instance, field_name, value)

        return instance

