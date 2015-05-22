from django.conf.urls import patterns, include

from rest_framework import routers
from tests.polls.views import PollViewSet, ChoiceViewSet

router = routers.SimpleRouter()
router.register(r'polls', PollViewSet)
router.register(r'choices', ChoiceViewSet)

urlpatterns = router.urls
