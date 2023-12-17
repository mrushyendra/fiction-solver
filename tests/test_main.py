from application.main import GameState


def test_correct_guess():
    game_state = GameState(
        word="hello",
        guesses=[],
        clues=[],
        checks=[],
    )
    guess = "hello"
    assert(game_state.guess(guess))
    assert(len(game_state.guesses) == 1)


def test_incorrect_guess():
    game_state = GameState(
        word="hello",
        guesses=[],
        clues=[],
        checks=[],
    )
    guess = "world"
    assert (game_state.guess(guess))
    assert (len(game_state.guesses) == 1)


def test_invalid_guess():
    game_state = GameState(
        word="hello",
        guesses=[],
        clues=[],
        checks=[],
    )
    guess = "longer_than_5_chars"
    assert (not game_state.guess(guess))
    assert (len(game_state.guesses) == 0)