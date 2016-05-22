from django.db import transaction
from django.db import IntegrityError
from django.shortcuts import render

from rest_framework.decorators import detail_route
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ValidationError
from rest_framework import status

from .models import Game
from .models import GamePlayer
from .models import Player

from .serializers import GameSerializer
from .serializers import PlayerSerializer
from .serializers import GuessSerializer


class GameViewSet(ModelViewSet):
    """This viewset automatically provides `list` and `detail` actions."""

    queryset = Game.objects.all()
    serializer_class = GameSerializer

    @detail_route(methods=['post', 'get'])
    def join(self, request, pk=None):
        game = self.get_object()
        if game.started:
            raise ValidationError("Game already started, you can't join now")
        if request.method == 'GET':
            serializer = PlayerSerializer(game.players, many=True)
        else:
            name = request.data.get('name')
            with transaction.atomic():
                try:
                    player = Player.objects.get(name=name)
                except Player.DoesNotExist:
                    serializer = PlayerSerializer(data=request.data)
                    serializer.is_valid(raise_exception=True)
                    player = serializer.save()
                else:
                    serializer = PlayerSerializer(instance=player)
                try:
                    GamePlayer.objects.create(game=game, player=player)
                except IntegrityError:
                    raise ValidationError(
                        "Player '{}' already in this game".format(name))
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @detail_route(methods=['post'])
    def guess(self, request, pk=None):

        game = self.get_object()
        if not game.started:
            raise ValidationError("Game has not started, you can't guess now")

        name = request.data.get('name')
        try:
            gameplayer = GamePlayer.objects.get(game=game,
                                                player__name=name)
        except GamePlayer.DoesNotExist:
            raise ValidationError(
                {'name': "Player '{}' is not in this game.".format(name)})

        if gameplayer.solved:
            raise ValidationError("You already solved this game.")

        serializer = GuessSerializer(gameplayer, data=request.data)
        serializer.is_valid(raise_exception=True)
        guess = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
