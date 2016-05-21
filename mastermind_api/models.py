import random
from threading import Event

from django.db import models

from .mastermind_engine import MastermindGameEngine


class Player(models.Model):

    name = models.CharField(max_length=128)

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

    num_guesses = models.PositiveIntegerField(
        default=0,
        editable=False)

    players = models.ManyToManyField(
        Player,
        blank=True,
        through='GamePlayer')

    solved = models.BooleanField(
        default=False,
        editable=False)

    _ready_events = {}

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
    def all_ready_event(self):
        try:
            return self._ready_events[self.pk]
        except KeyError:
            self._ready_events[self.pk] = Event()
            return self._ready_events[self.pk]


class GamePlayer(models.Model):

    game = models.ForeignKey(Game)

    player = models.ForeignKey(Player)

    guess = models.PositiveIntegerField()

    class Meta:
        unique_together = ('game', 'player')
