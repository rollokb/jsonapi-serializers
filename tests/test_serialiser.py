import pdb
import json

from django.test import TestCase
from django.test.client import RequestFactory

from rest_framework.renderers import JSONRenderer


from .polls.serializers import PollSerializer, ChoiceSerializer, AlternatePollSerializer
from .polls.models import *




class SerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.poll = Poll.objects.create(question="p1")
        
        c1 = Choice.objects.create(poll=cls.poll, choice_text="c1", votes=0)
        c2 = Choice.objects.create(poll=cls.poll, choice_text="c2", votes=0)
        c3 = Choice.objects.create(poll=cls.poll, choice_text="c3", votes=0)
        
        cls.choice = c1

        factory = RequestFactory()
        cls.request = factory.get('/')
    
    def test_normal_serializer(self):
        alt_serializer = AlternatePollSerializer(self.poll, context={'request': self.request})

        poll_json = json.dumps(alt_serializer.data, sort_keys=True, indent=2)
        packed_json = json.loads(poll_json)
        packed_json['choices'].pop()


        new_alt_serializer = AlternatePollSerializer(self.poll, data=packed_json, partial=False, context={'request': self.request})

        new_alt_serializer.is_valid(raise_exception=True)



        pdb.set_trace()
        new_alt_serializer.save()

        new_poll_json = json.dumps(new_alt_serializer.data, sort_keys=True, indent=2)
        print(new_poll_json)



    def test1(self):
        """TODO: Docstring for test1.
        :returns: TODO

        """

        ser1 = ChoiceSerializer(self.choice, context={'request': self.request })
        #print(json.dumps(ser1.data, sort_keys=True, indent=2))

    def test_many_related_json_api_field_read(self):
        poll_serializer = PollSerializer(self.poll, context={'request': self.request})
        poll_json = json.dumps(poll_serializer.data, sort_keys=True, indent=2)
        
        self.poll_json = poll_json

    def test_many_related_json_api_field_write(self):


        poll_serializer = PollSerializer(self.poll, context={'request': self.request})
        poll_json = json.dumps(poll_serializer.data, sort_keys=True, indent=2)

        packed_json = json.loads(poll_json)
        
        packed_json['choices']['data'].pop()


        new_poll_serializer = PollSerializer(self.poll, data=packed_json, partial=False)
        new_poll_serializer.is_valid(raise_exception=True)


        new_poll_serializer.save()

        new_poll_json = json.dumps(new_poll_serializer.data, sort_keys=True, indent=2)

    


#   def update(self, request, *args, **kwargs):
#       partial = kwargs.pop('partial', False)
#       instance = self.get_object()
#       serializer = self.get_serializer(instance, data=request.data, partial=partial)
#       serializer.is_valid(raise_exception=True)
#       self.perform_update(serializer)
#       return Response(serializer.data)

#   def perform_update(self, serializer):
#       serializer.save()
 

