# jsonapi-serializers

JSON API Serializers is a module for Django Rest Framework that makes it easier to create RelatedObject fields which need to be wrapped in data.

So far, usage.

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

# Future goals

To be able to have a generic wrapping syntax that allows you wrap any RelatedField in in JSONAPIField, and proxy it's methods. Also creating a serializer for grouping of realtions and attributes. 

The end goal is to have a simple module that makes doing things like [this](http://jsonapi.org/) simple to create without sacraficing control over serialization.
