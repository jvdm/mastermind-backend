from django.core.urlresolvers import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APITestCase

from .mastermind_engine import MastermindGameEngine
from .models import Game


class MastermindGameEngineTest(TestCase):

    def test_evaluate_guess(self):
        secret = "ABCDEFGH"
        ge = MastermindGameEngine(secret)
        result = ge.evaluate_guess("ABCDAAAA")
        self.assertEqual(result, (4, 0))

        result = ge.evaluate_guess("ABCDAAAE")
        self.assertEqual(result, (4, 1))

        result = ge.evaluate_guess(secret)
        self.assertEqual(result, (len(secret), 0))

        result = ge.evaluate_guess(list(reversed(secret)))
        self.assertEqual(result, (0, len(secret)))


class APITestCase(APITestCase):

    def test_should_create_game(self):
        resp = self.client.post(reverse('game-list'),
                                {'player_count': 1},
                                format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Game.objects.count(), 1)

    def test_should_wait_players_to_join(self):
        players = 5
        resp = self.client.post(reverse('game-list'),
                                {'player_count': players},
                                format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Game.objects.count(), 1)
