import random
from dataclasses import dataclass
from math import floor
from typing import Optional

from word_list import word_list


# An implementation of https://www.allplay.com/board-games/fiction/:
#
# Fiction is a Wordle-inspired game of deception. One player is the Lie-brarian and will
# choose a secret word. The other players will, as a team, use logic and literacy to deduce
# the secret word as quickly as possible.
#
# Players have ten guesses to deduce the secret word, but beware! The Lie-brarian's clues
# will always contain exactly one lie. The Guessers win if they figure out the word; the
# Lie-brarian wins if the time or number of guesses runs out.
#
# Players have the option of using 3 "fact-or-fiction" tokens to challenge exactly one
# letter in a Lie-brarian's clue. The lie-brarian must reveal whether the clue for that
# letter is true or false.

@dataclass
class GameState:
    word: str
    guesses: list[str]
    clues: list[str]
    # list of fact-or-fiction checks, each check is a tuple of (guess number, letter, is_true)
    checks: list[tuple[int, int, bool]]

    def guess(self, guess: str) -> bool:
        if len(guess) != 5:
            print("Guess must be 5 letters long")
            return False
        self.guesses.append(guess)
        return True

    def clue(self, clue: str) -> bool:
        if any(c not in "XY~" for c in clue):
            print("Clue must be a string of X, Y, or ~")
            return False
        if len(clue) != 5:
            print("Clue must be 5 letters long")
            return False

        guess = self.guesses[-1]
        # Build up the correct clue from the guess first
        correct_clue = ""
        for i, c in enumerate(guess):
            if c == self.word[i]:
                correct_clue += "Y"
            elif c not in self.word:
                correct_clue += "X"
            else: # c exists somewhere else in the word
                word_char_count = self.word.count(c)
                guess_char_count = guess.count(c)
                if guess_char_count == 1:
                    correct_clue += "~"
                else: # guess_char_count > 1
                    def num_guesses_of_that_char_correct(word, guess, c):
                        return sum(1 for j, char in enumerate(word) if char == c and guess[j] == c)

                    def num_guesses_of_that_char_incorrect_before_current(word, guess, c, i):
                        return sum(1 for j, char in enumerate(guess) if char == c and word[j] != c and j < i)

                    # Follows wordle rules. If the same character occurs multiple times in a guess, the guess characters
                    # that occur in the correct positions are marked correct ('Y'). From left-to-right, the remaining
                    # guess characters are marked with a ('~') if the word contains that character elsewhere, and there
                    # hasn't already been a previous ('~') allocated for that character. Otherwise, the character is
                    # marked incorrect ('X').
                    num_squiggles_left = (word_char_count - num_guesses_of_that_char_correct(self.word, guess, c)
                                          - num_guesses_of_that_char_incorrect_before_current(self.word, guess, c, i))
                    if num_squiggles_left > 0:
                        correct_clue += "~"
                    else:
                        correct_clue += "X"

        num_lies: int = sum(1 if c != correct_clue[i] else 0 for i, c in enumerate(clue))
        if num_lies != 1:
            print(f"Clue must contain exactly one lie. Your clue had {num_lies} lies.")
            return False

        self.clues.append(clue)
        return True

    # check the (0-indexed) letter in the most recent clue
    def check(self, position: int) -> None:
        if len(self.checks) >= 3:
            print("You're out of fact-or-fiction checks!")
            return
        if position >=5 or position < 0:
            print("Position must be between 1 and 5")
            return

        clue = self.clues[-1][position]
        guess = self.guesses[-1][position]
        fact = True
        match clue:
            case "X":
                if guess in self.word:
                    fact = False
                    print("Fiction")
                else:
                    print("Fact")
            case "Y":
                if guess == self.word[position]:
                    print("Fact")
                else:
                    fact = False
                    print("Fiction")
            case "~":
                if clue in self.word and self.word[position] != clue:
                    print("Fact")
                else:
                    fact = False
                    print("Fiction")
        check = (len(self.guesses), position, fact)
        self.checks.append(check)

    def is_game_over(self) -> bool:
        if self.guesses and self.guesses[-1] == self.word:
            print("Guessers win!")
            return True
        if len(self.guesses) >= 10:
            print("Librarian wins!")
            return True
        return False


def play() -> None:
    word: Optional[str] = None
    while not word:
        word = input("Lie-brarian, type a 5 letter word. To use a random word instead, press enter.\n")
        if len(word) == 0:
            word = word_list[floor(random.Random().random() * len(word_list))]
            print(f"Your word is: {word}")
        elif len(word) != 5:
            word = ""
            print("Word must be 5 letters long. Please try again.")

    game_state = GameState(
        word=word,
        guesses=[],
        clues=[],
        checks=[],
    )

    while True:
        while True:
            guess = input(f"Attempt #{len(game_state.guesses) + 1}. Guess a word: ")
            if game_state.guess(guess):
                break
        if game_state.is_game_over():
            break

        while True:
            clue = input("Enter a clue: ")
            if game_state.clue(clue):
                break

        check = input("To perform a fact-or-fiction check, enter the position of the letter in the clue, (e.g. 1, 2, 3)"
                      ". Leave blank to skip.")
        if check:
            game_state.check(int(check) - 1)


if __name__ == "__main__":
    play()
