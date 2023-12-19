import pytest

from application.main import GameState


@pytest.mark.parametrize("word, is_valid, num_guesses",
                         [("hello", True, 1),
                          ("world", True, 1),
                          ("longer_than_5_chars", False, 0),
                          ("HeLlO", True, 1) # case insensitive
                         ])
def test_guess(word, is_valid, num_guesses):
    game_state = GameState(
        word="hello",
        guesses=[],
        clues=[],
        checks={},
    )
    guess = word
    assert (game_state.guess(guess) == is_valid)
    assert (len(game_state.guesses) == num_guesses)


@pytest.mark.parametrize("word, guess, clue, is_valid, num_clues",
                         [("world", "world", "YYYYX", True, 1),
                          ("world", "world", "YYYY~", True, 1),
                          ("world", "world", "YY~YY", True, 1),
                          ("world", "world", "YXYYX", False, 0), # more than 1 lie
                          ("world", "world", "YYYYa", False, 0), # invalid character
                          ("world", "world", "YYYY", False, 0), # too short
                          ("world", "world", "~Y~~Y", False, 0), # more than 1 lie
                          ("banal", "annal", "~XYYY", False, 0), # no lies
                          ("banal", "annal", "~~YYY", True, 1),
                          ("banal", "union", "X~XXX", False, 0), # no lies
                          ("banal", "union", "XYXX~", False, 0), # more than 1 lie
                          ("banal", "alloy", "~~XXX", False, 0), # no lies
                          ("banal", "allow", "Y~XXX", True, 1),
                          ("banal", "banal", "YYXYY", True, 1),
                          ])
def test_clue(word, guess, clue, is_valid, num_clues):
    game_state = GameState(
        word=word,
        guesses=[guess],
        clues=[],
        checks={},
    )
    assert (game_state.clue(clue) == is_valid)
    assert (len(game_state.clues) == num_clues)