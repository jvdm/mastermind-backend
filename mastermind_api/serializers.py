from django.db import transaction

from rest_framework import serializers

from .models import Game
from .models import Player
from .models import PlayerOnGame


class GameSerializer(serializers.ModelSerializer):

    players_count = serializers.IntegerField(
        min_value=1, default=1)

    class Meta:
        model = Game
        fields = ('created_at', 'players_count', 'players')


class CreateGameSerializer(GameSerializer):

    owner = serializers.CharField()

    class Meta:
        fields = ('created_at', 'players_count', 'players', 'owner')

    def create(self, validated_data):
        owner = validated_data.pop('owner')
        with transaction.atomic():
            game = super().create(validated_data)
            player, _ = Player.objects.get_or_create(name=owner)
            PlayerOnGame.objects.create(
                game=game, player=player,
                has_joined=False, is_owner=True)
        return game
