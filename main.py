from dataclasses import dataclass
from typing import Optional


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

        num_lies: int = 0
        guess = self.guesses[-1]
        for i, c in enumerate(clue):
            match c:
                case 'X':
                    if guess[i] in self.word:
                        num_lies += 1
                case 'Y':
                    if guess[i] != self.word[i]:
                        num_lies += 1
                case '~':
                    if guess[i] == self.word[i] or guess[i] not in self.word:
                        num_lies += 1
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
        word = input("Lie-brarian, pick a 5 letter word:")
        if len(word) != 5:
            print("Word must be 5 letters long. Please try again.")
            continue

    game_state = GameState(
        word=word,
        guesses=[],
        clues=[],
        checks=[],
    )

    while True:
        while True:
            guess = input(f"Attempt #{len(game_state.guesses)}. Guess a word: ")
            if game_state.guess(guess):
                break
        if game_state.is_game_over():
            break

        while True:
            clue = input("Enter a clue: ")
            if game_state.clue(clue):
                break

        check = input("Enter a fact-or-fiction check for a position in the clue (e.g. 1, 2, 3). Leave blank to skip. ")
        if check:
            game_state.check(int(check) - 1)


if __name__ == "__main__":
    play()
