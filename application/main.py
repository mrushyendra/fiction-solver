import random
import time
from dataclasses import dataclass
from enum import Enum
from math import floor
from typing import Optional

from application.solver import initialize_solution_space, Solver
from application.word_list import word_list


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
    # A map of fact-or-fiction checks, from 0-indexed guess number to a tuple of (0-indexed letter position, is_true)
    checks: dict[int, tuple[int, bool]]
    known_char: str

    def guess(self, guess: str) -> bool:
        guess = guess.lower()
        if len(guess) != 5:
            print("Guess must be 5 letters long")
            return False
        self.guesses.append(guess)
        return True

    def generate_correct_clue(self, guess: str) -> str:
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
        return correct_clue

    def clue(self, clue: str) -> bool:
        if any(c not in "XY~" for c in clue):
            print("Clue must be a string of X, Y, or ~")
            return False
        if len(clue) != 5:
            print("Clue must be 5 letters long")
            return False

        guess = self.guesses[-1]
        # Build up the correct clue from the guess first
        correct_clue = self.generate_correct_clue(guess)

        num_lies: int = sum(1 if c != correct_clue[i] else 0 for i, c in enumerate(clue))
        if num_lies != 1:
            print(f"Clue must contain exactly one lie. Your clue had {num_lies} lies.")
            return False

        self.clues.append(clue)
        return True

    def has_checks_remaining(self) -> bool:
        return len(self.checks) < 3

    # check the (0-indexed) letter in the most recent clue. Returns the checked position and whether the
    # corresponding clue was true or false (i.e. a lie).
    def check(self, position: int) -> Optional[tuple[int, bool]]:
        if len(self.checks) >= 3:
            print("You're out of fact-or-fiction checks!")
            return None
        if position >=5 or position < 0:
            print("Position must be between 1 and 5 inclusive")
            return None

        clue = self.clues[-1]
        guess = self.guesses[-1]
        correct_clue = self.generate_correct_clue(guess)
        if correct_clue[position] != clue[position]:
            print("Fiction")
            self.checks[len(self.guesses) - 1] = (position, False)
        else:
            print("Fact")
            self.checks[len(self.guesses) - 1] = (position, True)
        return self.checks[len(self.guesses) - 1]

    def is_game_over(self) -> bool:
        if self.guesses and self.guesses[-1] == self.word:
            print("Guessers win!")
            return True
        if len(self.guesses) >= 10:
            print("Librarian wins!")
            return True
        return False

    def __str__(self):
        guesses_str = ""
        for i, (guess, clue) in enumerate(zip(self.guesses, self.clues)):
            guesses_str += f"#{i + 1}: {guess}\n"
            guesses_str += f"#{i + 1}: {clue}\n"
            if self.checks.get(i):
                position, is_true = self.checks[i]
                is_fact = "Fact" if is_true else "Fiction"
                guesses_str += f"#{i + 1}: Clue for '{guess[position]}' at position {position + 1} is {is_fact}\n"

        return (f"-----------------------\n"
                f"Number of guesses: {len(self.guesses)}\n"
                f"Known character: {self.known_char}\n"
                f"{guesses_str}"
                f"-----------------------")


class AssistanceLevel(Enum):
    NO_ASSISTANCE = 0
    # Provide diagnostic information to guessers, such as the list of words compatible
    # with the current guesses and clues.
    HYBRID = 1
    # All guessing is done by the solver
    FULLY_AUTOMATED = 2


class Side(Enum):
    LIBRARIAN = 1
    GUESSER = 2
    BOTH = 3


def play() -> None:
    side: Optional[Side] = None
    while not side:
        try:
            side = Side(int(input("Welcome! Pick a side. To play as a librarian, enter '1'. To play as a guesser,"
                                  " enter '2'. To play both sides, enter '3'.\n")))
        except ValueError:
            print("Invalid input. Please try again.")
            continue
    print(f"Playing as {side.name}")
    print("----------------------------")

    word: Optional[str] = None
    while not word:
        if side != Side.GUESSER:
            word = input("Librarian, enter a 5 letter word. To use a random word instead, leave blank: ")

        if not word or len(word) == 0:
            word = word_list[floor(random.Random().random() * len(word_list))]
        elif len(word) != 5:
            word = ""
            print("Word must be 5 letters long. Please try again.\n")
        elif word not in word_list:
            word = ""
            print("Word must be in the accepted Wordle word list. Please try again.\n")
    if side != Side.GUESSER:
        print(f"Your word is: {word}")

    known_char: Optional[str] = None
    if side != Side.GUESSER:
        while not known_char:
            known_char = input("Librarian, enter a character confirmed to be in the word: ")
            if len(known_char) != 1 or known_char not in word:
                known_char = ""
                print("Known character must be a single character in the word. Please try again.")
    else:
        known_char = word[random.randint(0, 4)]
    print(f"Starting clue: `{known_char}` exists in the word.")
    print("----------------------------")

    print("Enter the level of AI-assistance you'd like to use:")
    assistance_level: Optional[AssistanceLevel] = None
    while assistance_level is None:
        try:
            assistance_level = AssistanceLevel(int(input("0: No assistance\n1: Hybrid\n2: Fully automated\n")))
        except ValueError:
            print("Invalid input. Please try again.\n")
    print(f"You've selected: {assistance_level.name}")
    print("----------------------------")

    print("Starting game in 3...")
    time.sleep(1)
    print("Starting game in 2...")
    time.sleep(1)
    print("Starting game in 1...")
    time.sleep(1)
    print("----------------------------")

    game_state = GameState(
        word=word.lower(),
        guesses=[],
        clues=[],
        checks={},
        known_char=known_char.lower(),
    )

    initial_solution_space = initialize_solution_space(known_char.lower())
    solver = Solver(word_list, initial_solution_space)

    while True:
        while True:
            if assistance_level == AssistanceLevel.FULLY_AUTOMATED or side == Side.LIBRARIAN:
                guess = solver.pick_guess()
                print(f"Attempt #{len(game_state.guesses) + 1}. The computer's guess: ", guess)
            else:
                guess = input(f"Attempt #{len(game_state.guesses) + 1}. Guess a word: ")
            if game_state.guess(guess):
                break
        if game_state.is_game_over():
            break

        while True:
            if assistance_level == AssistanceLevel.FULLY_AUTOMATED or side == Side.GUESSER:
                clue = solver.pick_clue(game_state.generate_correct_clue(guess))
                print("The computer's clue: ", clue)
            else:
                clue = input("Enter a clue: ")
            if game_state.clue(clue):
                break

        fact_or_fiction_check = None
        if game_state.has_checks_remaining():
            if ((assistance_level == AssistanceLevel.HYBRID or assistance_level == AssistanceLevel.NO_ASSISTANCE)
                    and side != Side.LIBRARIAN):
                check = input("To perform a fact-or-fiction check, enter the position of the letter in the clue,"
                              " (e.g. 1, 2, 3). Leave blank to skip: ")
            # Choose whether to fact-or-fiction check because AssistanceLevel.FULLY_AUTOMATED or side == Side.LIBRARIAN
            else:
                # We could be smarter here, but instead just check a random letter in every 3rd clue for now.
                if len(game_state.clues) % 3 == 0:
                    check = random.randint(1,5)
                    print(f"Automatically checking position {check}")
                else:
                    check = None
            if check:
                fact_or_fiction_check = game_state.check(int(check) - 1)

        if assistance_level != AssistanceLevel.NO_ASSISTANCE:
            solver.expand_solution_spaces(guess, clue, fact_or_fiction_check)

        print(game_state)


if __name__ == "__main__":
    play()
