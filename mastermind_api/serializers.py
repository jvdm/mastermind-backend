from django.db import transaction

from rest_framework import serializers

from .models import Game
from .models import Player


class GameSerializer(serializers.ModelSerializer):

    players_count = serializers.IntegerField(
        min_value=1, default=1)

    class Meta:
        model = Game
        fields = ('created_at', 'players_count', 'players')


class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player

    def save(self, game=None):
        if game:
            self.game = game
        return super().save()

    def create(self, validated_data):
        with transaction.atomic():
            player = super().create(validated_data)
            self.game.players.add(player)
        return player
