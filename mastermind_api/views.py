from django.db import transaction
from django.db import IntegrityError
from django.shortcuts import render

from rest_framework.decorators import detail_route
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ValidationError

from .models import Game
from .models import GamePlayer
from .models import Player
from .serializers import GameSerializer
from .serializers import PlayerSerializer
from .models import GamePlayer
from .models import Guess


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
        return Response(serializer.data)

    @detail_route(methods=['post'])
    def guess(self, request, pk=None):
        game = self.get_object()
        if not game.started:
            raise ValidationError("Game already started, you can't join now")
        code = request.data['code']
        name = request.data['name']

        if not set(code).issubset(Game.COLORS):
            raise ValidationError("code with invalid color '{}'".format(code))
        if len(code) < len(game.secret):
            raise ValidationError("code '{}' is too short".format(code))
        if len(code) > len(game.secret):
            raise ValidationError("code '{}' is too big".format(code))
        try:
            gameplayer = GamePlayer.objects.get(game=game,
                                                player__name=name)
        except GamePlayer.DoesNotExists:
            raise ValidationError("name {} is not valid for this "
                                  "game".format(name))
        if game.round != gameplayer.guesses.count():
            raise ValidationError("cannot make a move yet")
        gameplayer.create_guess(code)
        exact, near = game.engine.evaluate_guess(code)
        return Response({'result': {'exact': exact,
                                    'near': near}})
