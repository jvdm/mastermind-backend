import random

from django.db import models

from threading import Event


class Player(models.Model):

    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Game(models.Model):

    """A mastermind game."""

    created_at = models.DateTimeField(
        auto_now_add=True)

    modified_at = models.DateTimeField(
        auto_now=True)

    secret = models.CharField(
        editable=False,
        max_length=256)

    players_count = models.PositiveIntegerField()

    players = models.ManyToManyField(
        Player, blank=True)

    _ready_events = {}

    def save(self, *args, **kwds):
        if self.pk is None:
            self.secret = ','.join(random.choice('abcdefgh')
                                   for _ in range(0, 8))
        super().save(*args, **kwds)

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
