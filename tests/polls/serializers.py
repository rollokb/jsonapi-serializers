from jsonapi_serializers.serializers import JSONAPISerializer, JSONAPIRelationField
from rest_framework import serializers
from tests.polls.models import *

from rest_framework.reverse import reverse

class ChoiceField(JSONAPIRelationField):
    def build_links(self):
        request = self.context.get('request', None)
        format = self.context.get('format', None)

        return {
            "collection": self.reverse('choice-list', request=request),
            "filtered_collection": "http://testserver/question/1/choices/",
            "instance": self.reverse('choice-list', request=request) + '${id}/'
        }

        

class AlternatePollSerializer(serializers.ModelSerializer):
    question = serializers.CharField()
    choices = serializers.HyperlinkedRelatedField(
        many=True,
        source='choice_set',
        queryset=Choice.objects.all(),
        view_name='choice-detail'
    )

    class Meta:
        model = Poll

class PollSerializer(JSONAPISerializer):
    question = serializers.CharField()
    choices = ChoiceField(
        many=True,
        source='choice_set',
        queryset=Choice.objects.all(),
    )

    class Meta:
        relation_fields = ['choices',]
        model = Poll

class ChoiceSerializer(JSONAPISerializer):
    poll = JSONAPIRelationField(
        type='poll',
        read_only=True
    )

    choice_text = serializers.CharField()
    votes = serializers.IntegerField()
    
    class Meta:
        model = Choice
        relation_fields = ['poll',]

