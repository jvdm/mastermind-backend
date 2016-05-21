from django.conf.urls import url
from django.conf.urls import include

from rest_framework.routers import DefaultRouter

from .views import GameViewSet


router = DefaultRouter()
router.register('games', GameViewSet)


urlpatterns = [
    url(r'^', include(router.urls))]
