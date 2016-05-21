from django.core.urlresolvers import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APITestCase

from .mastermind_engine import MastermindGameEngine
from .models import Game
from .models import GamePlayer


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

    def _join(self, game_id, player):
        resp = self.client.post(reverse('game-join', kwargs={'pk': game_id}),
                                {'name': player})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        return resp

    def _guess(self, game_id, player, code):
        resp = self.client.post(reverse('game-guess', kwargs={'pk': game_id}),
                                {'name': player,
                                 'code': code})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        return resp

    def test_should_create_game(self):
        resp = self.client.post(reverse('game-list'),
                                {'player_count': 1},
                                format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Game.objects.count(), 1)

    def test_should_wait_players_to_join(self):

        players_count = 2

        resp = self.client.post(reverse('game-list'),
                                {'players_count': players_count},
                                format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Game.objects.count(), 1)

        join_url = reverse('game-join', kwargs={'pk': resp.data['id']})

        resp = self.client.post(join_url,
                                {'name': 'jvdm'},
                                format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data, {'name': 'jvdm'})

        resp = self.client.post(join_url,
                                {'name': 'jvdm'},
                                format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        resp = self.client.post(join_url,
                                {'name': 'fenf'},
                                format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data, {'name': 'fenf'})

        self.assertEqual(GamePlayer.objects.count(), 2)

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

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_increment_round(self):
        resp = self.client.post(reverse('game-list'),
                                {'players_count': 2},
                                format='json')

        game_id = resp.data['id']

        self._join(game_id, 'foo')
        self._join(game_id, 'bar')

        self._guess(game_id, 'foo', 'abcdefgh')
        resp = self.client.post(reverse('game-guess', kwargs=dict(pk=id)),
                                {'code': 'abcdefgh',
                                 'name': 'foo'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        self._guess(game_id, 'bar', 'abcdefgh')
        self._guess(game_id, 'foo', 'abcdefgh')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
