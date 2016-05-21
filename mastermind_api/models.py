import random

from django.db import models


class Game(models.Model):
    """A mastermind game."""

    COLORS = ('red', 'orange', 'yellow', 'blue',
              'purple', 'brown', 'gray', 'magenta',
              'mahogany', 'peach', 'pink', 'mango')

    created_at = models.DateTimeField(
        auto_now_add=True)

    modified_at = models.DateTimeField(
        auto_now=True)

    secret = models.CharField(
        editable=False,
        max_length=256)

    def save(self, *args, **kwds):
        if self.pk is None:
            self.secret = ','.join(random.choice(self.COLORS)
                                   for _ in range(0, 8))
        super().save(*args, **kwds)
