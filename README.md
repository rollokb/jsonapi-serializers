# JSON.api-serializers

A JSON RESTful API usual requires a more complex output than what `djangorestframework` normally give you. This module is born out of my attempt at making building API's that follow the [jsonapi.org](jsonapi.org), standard. 

## Summary

This module builds on django-rest-framework's serializers to allow for a more compositional approach to defining serializers.

Currently `JSON.api-serializers` adds two new features. `BaseProxyRelationalField` which allows you to wrap a field in an arbitrary dictionary, while maintaining read/write abilities. It also adds a serializer `GroupedSerializer` that allows you to build serializers in a more compositional manner without sacrificing read/write capabilities.



## Install

Right now install from Github with
    
    pip install -e https://github.com/rollokb/jsonapi-serializers

## GroupedSerializer

    class ExampleProductSerializer(GroupedSerializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        date_created = serializers.DateField()
        date_modified = serializers.DateField()
        
        def set_composition(self):
            self.composition = Composition(
                {
                    "attributes": self.create_field_group(['name', 'id',]),
                    "dates":self.create_field_group(['date_created', 'date_modified',])
                }
            )
        
        class Meta:
            model = ExampleProduct

This will wrap the fields in "attributes" and "dates" fields, outputting this

    {
        "attributes": {
            "name": "Example Product",
            "id": 23
        },
        "dates": {
            "date_created": "Feb 11 '14 14:03",
            "date_modified": "Feb 11 '14 15:03",
        }
    }

Unlike using a serializer method field, the fields remain writable.

## BaseProxyRelationField/HyperlinkedProxyRelationalField

Is a field which allows you to wrap individual fields in arbitrary JSON while staying writable.

    class ChoiceField(JSONAPIRelationField):
        def build_links(self):
            request = self.context.get('request', None)
            format = self.context.get('format', None)

            return {
                "collection": self.reverse('choice-list', request=request),
                "filtered_collection": "http://testserver/question/1/choices/",
                "instance": self.reverse('choice-list', request=request) + '${id}/'
            }


    class PollSerializer(serializers.ModelSerializer):
        question = serializers.CharField()
        choices = ChoiceField(
            many=True,
            source='choice_set',
            queryset=Choice.objects.all(),
        )

        class Meta:
            model = Poll

This will output something like

    {
      "choices": {
        "data": [
          1,
          2,
          3
        ],
        "links": {
          "collection": "/choices/",
          "filtered_collection": "http://testserver/question/1/choices/",
          "instance": "/choices/${id}/"
        }
      },
      "id": 1,
      "question": "p1"
    }

The end goal is to have a simple module that makes doing things like [this](http://jsonapi.org/) simple to create without sacrificing control over serialization.


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/rollokb/jsonapi-serializers/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

