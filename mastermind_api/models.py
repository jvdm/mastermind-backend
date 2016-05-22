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

    _engines = {}

    def save(self, *args, **kwds):
        is_creating = self.pk is None
        if is_creating:
            self.secret = ''.join(random.choice(list(self.COLORS))
                                  for _ in range(0, 8))
        super().save(*args, **kwds)

    def __str__(self):
        return str(self.id)

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

    @property
    def is_solved(self):
        return self.gameplayer_set.filter(solved=True).exists()


class GamePlayer(models.Model):

    game = models.ForeignKey(Game)

    player = models.ForeignKey(Player)

    solved = models.BooleanField(
        default=False,
        editable=False)

    class Meta:
        unique_together = ('game', 'player')

    @property
    def can_guess(self):
        return self.game.round == self.guess_set.count()

    def __str__(self):
        return '{} playing {}'.format(self.player, self.game)


class Guess(models.Model):

    game_player = models.ForeignKey(
        GamePlayer)

    code = models.CharField(
        max_length=64)

    exact = models.PositiveIntegerField(
        editable=False)

    near = models.PositiveIntegerField(
        editable=False)

    created_at = models.DateTimeField(
        auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwds):

        assert self.pk is None

        with transaction.atomic():
            super().save(*args, **kwds)

            if self.exact == len(self.game_player.game.COLORS):
                self.game_player.solved = True
                self.game_player.save()

            # FIXME This could probably be done all in the RDBMS
            #       using aggregation, just be patient and go read
            #       the django docs.
            for gp in GamePlayer.objects \
                                .exclude(player=self.game_player.player) \
                                .filter(solved=False,
                                        game=self.game_player.game):
                if gp.can_guess:
                    break
            else:
                # Everybody has guessed, bump the game round.
                self.game_player.game.round += 1
                self.game_player.game.save()

    def __str__(self):
        return "'{}' from {} with exact {} and near {}" \
            .format(self.code, self.game_player,
                    self.exact, self.near)
