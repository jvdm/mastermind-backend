from django.conf.urls import url
from django.conf.urls import include

from rest_framework.routers import DefaultRouter

from .views import GameViewSet
from .views import mastermind
from .views import mastermind_hub

router = DefaultRouter()
router.register('games', GameViewSet)


urlpatterns = [
    url(r'^mastermind_hub/$', mastermind_hub),
    url(r'^mastermind/(?P<gameid>\d+)/(?P<name>.+)/$', mastermind),
    url(r'^', include(router.urls))]
