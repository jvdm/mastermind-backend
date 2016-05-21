from django.db import transaction

from rest_framework import serializers

from .models import Game
from .models import Player
from .models import GamePlayer


class GameSerializer(serializers.ModelSerializer):

    players_count = serializers.IntegerField(
        min_value=1, default=1)

    colors = serializers.SerializerMethodField()

    code_length = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ('id', 'created_at', 'players_count', 'players', 'colors',
                  'code_length', 'round', 'solved')
        read_only_fields = ('id', 'colors')

    def get_colors(self, obj):
        return list(obj.COLORS)

    def get_code_length(self, obj):
        return len(obj.COLORS)



class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player

    def save(self, game=None):
        if game:
            self.game = game
        return super().save()

    def create(self, validated_data):
        with transaction.atomic():
            name = validated_data.pop('name')
            player, _ = self.Meta.model.objects.get_or_create(
                name=name,
                defaults=validated_data)
            GamePlayer.objects.create(game=self.game, player=player)
        return player
