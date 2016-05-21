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

    def test_should_not_allow_guess_outside_round(self):
        resp = self.client.post(reverse('game-list'),
                                {'player_count': 1},
                                format='json')

        id = resp.data['id']
        resp = self.client.post(reverse('game-join', kwargs=dict(pk=id)),
                                {'name': 'foo'})

        resp = self.client.post(reverse('game-join', kwargs=dict(pk=id)),
                                {'name': 'bar'})

        resp = self.client.post(reverse('game-guess', kwargs=dict(pk=id)),
                                {'code': 'abcdefgh',
                                 'name': 'foo'})

        resp = self.client.post(reverse('game-guess', kwargs=dict(pk=id)),
                                {'code': 'aaaaaaaa',
                                 'name': 'foo'})

        self.assertIn('cannot make a move', resp.data[0])

    def test_should_increment_round(self):
        resp = self.client.post(reverse('game-list'),
                                {'player_count': 1},
                                format='json')

        id = resp.data['id']
        resp = self.client.post(reverse('game-join', kwargs=dict(pk=id)),
                                {'name': 'foo'})

        resp = self.client.post(reverse('game-join', kwargs=dict(pk=id)),
                                {'name': 'bar'})

        resp = self.client.post(reverse('game-guess', kwargs=dict(pk=id)),
                                {'code': 'abcdefgh',
                                 'name': 'foo'})
        resp = self.client.post(reverse('game-guess', kwargs=dict(pk=id)),
                                {'code': 'abcdefgh',
                                 'name': 'foo'})
        self.assertIn('cannot make a move', resp.data[0])

        # bar makes a move now
        resp = self.client.post(reverse('game-guess', kwargs=dict(pk=id)),
                                {'code': 'abcdefgh',
                                 'name': 'bar'})

        # and now foo can make a move again
        resp = self.client.post(reverse('game-guess', kwargs=dict(pk=id)),
                                {'code': 'abcdefgh',
                                 'name': 'foo'})
        self.assertIn('result', resp.data)