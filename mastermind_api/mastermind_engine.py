from itertools import compress


class MastermindGameEngine:

    def __init__(self, secret):
        self.secret = secret

    def evaluate_guess(self, guess):
        assert len(guess) == len(self.secret)
        correct_num = sum((map((lambda x, y: x == y), self.secret, guess)))
        incorrect_filter = list(map((lambda x, y: x != y), self.secret, guess))
        remaining_secret = list(compress(self.secret, incorrect_filter))
        incorrect_guesses = list(compress(guess, incorrect_filter))

        incorrect_guesses_num = 0
        for g in incorrect_guesses:
            if g in remaining_secret:
                remaining_secret.remove(g)
                incorrect_guesses_num += 1

        return correct_num, incorrect_guesses_num

    def hint(self, guess):
        for i in range(len(guess)):
            if guess[i] != self.secret[i]:
                return i, self.secret[i]
        return None
