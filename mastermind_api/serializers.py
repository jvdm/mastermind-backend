from django.db import transaction

from rest_framework import serializers

from .models import Game
from .models import Player
from .models import Guess
from .models import GamePlayer


class GameSerializer(serializers.ModelSerializer):

    players_count = serializers.IntegerField(
        min_value=1, default=1)

    colors = serializers.SerializerMethodField()

    code_length = serializers.SerializerMethodField()

    solved = serializers.SerializerMethodField()

    players = serializers.StringRelatedField(many=True)

    class Meta:
        model = Game
        fields = ('id', 'created_at', 'players_count', 'players', 'colors',
                  'code_length', 'round', 'solved')
        read_only_fields = ('id', 'colors')

    def get_colors(self, obj):
        return list(obj.COLORS)

    def get_code_length(self, obj):
        return len(obj.COLORS)

    def get_solved(self, obj):
        return obj.is_solved


class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = ('name',)


class GamePlayerSerializer(serializers.ModelSerializer):

    player = serializers.StringRelatedField()

    class Meta:
        model = GamePlayer
        fields = ('game', 'player')


class GuessSerializer(serializers.ModelSerializer):

    past_results = serializers.SerializerMethodField()

    num_guesses = serializers.SerializerMethodField()

    solved = serializers.SerializerMethodField()

    class Meta:
        model = Guess
        fields = ('code', 'exact', 'near', 'created_at', 'past_results',
                  'num_guesses', 'solved')

    def __init__(self, gameplayer, *args, **kwds):
        self.gameplayer = gameplayer
        super().__init__(*args, **kwds)

    def get_past_results(self, obj):
        queryset = self.Meta.model.objects.filter(game_player=obj.game_player)
        return [{'code': g.code,
                 'exact': g.exact,
                 'near': g.near} for g in queryset]

    def get_num_guesses(self, obj):
        return self.Meta.model.objects.filter(game_player=obj.game_player).count()

    def get_solved(self, obj):
        return obj.game_player.solved

    def validate_code(self, code):
        if not set(code).issubset(self.gameplayer.game.COLORS):
            raise serializers.ValidationError("unknown color '{}'".format(code))
        if len(code) < len(self.gameplayer.game.secret):
            raise serializers.ValidationError("code '{}' is too short".format(code))
        if len(code) > len(self.gameplayer.game.secret):
            raise serializers.ValidationError("code '{}' is too big".format(code))
        return code

    def validate(self, data):
        if not self.gameplayer.can_guess:
            raise serializers.ValidationError(
                "Can't guess, the turn is not over.")
        return data

    def create(self, validated_data):
        exact, near = self.gameplayer \
                          .game \
                          .engine \
                          .evaluate_guess(validated_data['code'])
        return self.Meta.model.objects.create(
            game_player=self.gameplayer,
            exact=exact,
            near=near,
            **validated_data)
