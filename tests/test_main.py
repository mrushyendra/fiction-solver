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
        known_char="h",
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
        known_char=word[0],
    )
    assert (game_state.clue(clue) == is_valid)
    assert (len(game_state.clues) == num_clues)

@pytest.mark.parametrize("word, guess, clue, check_position, expected",
                         [("world", "world", "YYYYX", 4, (4, False)),
                          ("world", "world", "YYYY~", 4, (4, False)),
                          ("world", "world", "YY~YY", 0, (0, True)),
                          ("banal", "annal", "~~YYY", 1, (1, False)),
                          ("banal", "allow", "Y~XXX", 2, (2, True)),
                          ("banal", "banal", "YYXYY", 0, (0, True))
                          ])
def test_valid_check(word, guess, clue, check_position, expected):
    game_state = GameState(
        word=word,
        guesses=[guess],
        clues=[clue],
        checks={},
        known_char=word[0],
    )
    game_state.check(check_position)
    assert(len(game_state.checks) == 1)
    assert(game_state.checks[0] == expected)


def test_invalid_check():
    game_state = GameState(
        word="hello",
        guesses=["hotel"],
        clues=["Y~XYX"],
        checks={},
        known_char="h",
    )
    game_state.check(5) # Out of bounds of the word
    assert(len(game_state.checks) == 0)


"""
Known character: t
#1: abate
#1: XXXYX
#2: amity
#2: XXXYX
#3: aorta
#3: XYYYX
#4: birth
#4: XYY~Y
#5: forth
#5: XYY~~
#6: north
#6: YYY~Y
#6: Clue for 'n' at position 1 is Fiction
#7: north
#7: YYY~Y
#8: north
#8: YYY~Y
#8: Clue for 'r' at position 3 is Fact
#9: north
#9: YYY~Y
"""