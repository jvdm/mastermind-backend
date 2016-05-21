from django.db import transaction
from django.shortcuts import render

from rest_framework.decorators import detail_route
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ValidationError

from .models import Game
from .models import Player
from .serializers import GameSerializer
from .serializers import PlayerSerializer


class GameViewSet(ModelViewSet):
    """This viewset automatically provides `list` and `detail` actions."""

    queryset = Game.objects.all()
    serializer_class = GameSerializer

    @detail_route(methods=['post', 'get'])
    def join(self, request, pk=None):
        game = self.get_object()
        if request.method == 'GET':
            serializer = PlayerSerializer(game.players, many=True)
        else:
            serializer = PlayerSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(game)
        return Response(serializer.data)
