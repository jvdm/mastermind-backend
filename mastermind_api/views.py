from django.db import transaction
from django.shortcuts import render

from rest_framework.decorators import detail_route
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Game
from .models import PlayerOnGame
from .serializers import GameSerializer


class GameViewSet(ModelViewSet):
    """This viewset automatically provides `list` and `detail` actions."""

    queryset = Game.objects.all()
    serializer_class = GameSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            game = serializer.save()

    @detail_route(methods=['get'])
    def join(self, request, pk):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(serializer.data)
