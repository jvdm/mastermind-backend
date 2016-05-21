import random
from django.db.models import Q
from django.db import transaction

from django.db import models

from .mastermind_engine import MastermindGameEngine


class Player(models.Model):

    name = models.CharField(
        max_length=128,
        unique=True)

    def __str__(self):
        return self.name


class Game(models.Model):

    """A mastermind game."""

    COLORS = set('abcdefgh')

    created_at = models.DateTimeField(
        auto_now_add=True)

    modified_at = models.DateTimeField(
        auto_now=True)

    secret = models.CharField(
        editable=False,
        max_length=256)

    players_count = models.PositiveIntegerField()

    round = models.PositiveIntegerField(
        default=0,
        editable=False)

    players = models.ManyToManyField(
        Player,
        blank=True,
        through='GamePlayer')

    solved = models.BooleanField(
        default=False,
        editable=False)

    _engines = {}

    def save(self, *args, **kwds):
        is_creating = self.pk is None
        if is_creating:
            self.secret = ''.join(random.choice(list(self.COLORS))
                                  for _ in range(0, 8))
        super().save(*args, **kwds)

    @property
    def engine(self):
        try:
            return self._engines[self.pk]
        except KeyError:
            engine = MastermindGameEngine(self.secret)
            self._engines[self.pk] = engine
            return engine

    @property
    def number_of_players(self):
        return self.players.count()

    @property
    def started(self):
        return self.number_of_players == self.players_count


class GamePlayer(models.Model):

    game = models.ForeignKey(Game)

    player = models.ForeignKey(Player)

    def create_guess(self, code):

        with transaction.atomic():
            g = Guess(code=code, game_player=self)
            other_players = self.game.players.filter(~Q(gameplayer=self))
            last_one = True
            for p in other_players:
                gp = GamePlayer.objects.get(player=p, game=self.game)
                if gp.guesses.count() == self.game.round:
                    # not the last one
                    last_one = False
            if last_one:
                self.game.round += 1
                self.game.save()
            g.save()

    class Meta:
        unique_together = ('game', 'player')


class Guess(models.Model):

    code = models.CharField(max_length=64)

    game_player = models.ForeignKey(GamePlayer,
                                    related_name='guesses')

    def __str__(self):
        return "{} - {}".format(self.game_player.player.name, self.code)
