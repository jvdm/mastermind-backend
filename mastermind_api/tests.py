from .mastermind_engine import MastermindGameEngine
from django.test import TestCase


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