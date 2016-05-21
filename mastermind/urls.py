from django.conf.urls import url
from django.conf.urls import include

import mastermind_api.urls


urlpatterns = (
    url(r'^', include(mastermind_api.urls)),)
