from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet

from .models import Game
from .serializers import GameSerializer


class GameViewSet(ModelViewSet):
    """This viewset automatically provides `list` and `detail` actions."""

    queryset = Game.objects.all()
    serializer_class = GameSerializer
