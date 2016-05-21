from django.db import transaction

from rest_framework import serializers

from .models import Game
from .models import Player


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
        fields = ('name',)
