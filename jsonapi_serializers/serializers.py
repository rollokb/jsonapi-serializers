from rest_framework import serializers

from rest_framework.utils.serializer_helpers import (
    ReturnDict, ReturnList, BoundField, NestedBoundField, BindingDict
)

from rest_framework.compat import OrderedDict, unicode_to_repr
from rest_framework.fields import *  # NOQA
from rest_framework.reverse import reverse
from rest_framework.relations import MANY_RELATION_KWARGS, ManyRelatedField, PKOnlyObject

from pdb import set_trace

import six
import copy

class _RenderDataMixin(object):
    def build_data(self, obj):
        return obj.pk

class JSONAPIManyRelationField(serializers.ManyRelatedField, _RenderDataMixin):
    def to_representation(self, iterable):
        request = self.context.get('request', None)
        data_array = [ self.child_relation.to_representation(value) for value in iterable ]
        

        return {
            "links": self.child_relation.build_links(),
            "data": data_array
        }


    def to_internal_value(self, data):
        return [
            self.child_relation.to_internal_value(item)
            for item in data['data']
        ]

class JSONAPIRelationField(serializers.RelatedField, _RenderDataMixin):
    type = None

    def to_representation(self, obj):
        return self.build_data(obj)

    def __init__(self, **kwargs):
        
        self.type = kwargs.pop('type', copy.deepcopy(self.type)) 
        self.reverse = reverse

        super(JSONAPIRelationField, self).__init__(**kwargs)



    @classmethod
    def many_init(cls, *args, **kwargs):

        list_kwargs = {'child_relation': cls(*args, **kwargs)}
        for key in kwargs.keys():
            if key in MANY_RELATION_KWARGS:
                list_kwargs[key] = kwargs[key]
        return JSONAPIManyRelationField(**list_kwargs)


    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(pk=data)
        except ObjectDoesNotExist:
            self.fail('does_not_exist', pk_value=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)



class JSONAPISerializer(serializers.ModelSerializer):
    pass
