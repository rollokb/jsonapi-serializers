from tests.polls.models import *
from tests.polls.serializers import PollSerializer, ChoiceSerializer

from rest_framework import viewsets, permissions


class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def perform_authentication(self, request):
        pass
    def check_permissions(self, request):
        pass


class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer 

    def perform_authentication(self, request):
        pass
    def check_permissions(self, request):
        pass
