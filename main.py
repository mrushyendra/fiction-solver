from dataclasses import dataclass

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

    def update_guess(self, guess: str) -> None:
        self.guesses.append(guess)

    def update_clue(self, clue: str) -> None:
        self.clues.append(clue)

def play() -> None:
    game_state = GameState(
        word="",
        guesses=[],
        clues=[],
        checks=[],
    )

    while not game_state.word:
        word = input("Lie-brarian, pick a 5 letter word:")
        if len(word) != 5:
            print("Word must be 5 letters long!")
            continue
        game_state.word = word

    while True:
        guess = input("Guess a word: ")
        game_state.update_guess(guess)
        if guess == game_state.word:
            print("Guessers win!")
            break

        clue = input("Enter a clue: ")
        game_state.update_clue(clue)
        print(clue)


if __name__ == "__main__":
    play()
