import copy
from dataclasses import dataclass
from typing import Optional


@dataclass
class SolutionSpace:
    # for position 0-4, a 26-element list of 0s or 1s indicating whether the letter corresponding to that index
    # could be in that position.
    possible: list[list[int]]
    # for positions 0-4, the letter (if any) that is confirmed to be in that position. If no letter is confirmed,
    # the value is None.
    confirmed: list[Optional[str]]

    def __str__(self):
        possible_chrs = [[chr(ord('a') + j) for j in range(26) if (self.possible[i][j] == 1)] for i in range(5)]
        return (f"Possible characters: {possible_chrs}\n"
                f"Confirmed characters: {self.confirmed}")


class IncompatibleClueError(Exception):
    pass


def initialize_solution_space() -> SolutionSpace:
    return SolutionSpace(
        possible=[[1 for _ in range(26)] for _ in range(5)],
        confirmed=[None for _ in range(5)],
    )


def expand(solution_space: SolutionSpace, guess: str, clue: str) -> list[SolutionSpace]:
    clue_chr_possibilities = ['Y', 'X', '~']
    new_clues = []
    for i, clue_chr in enumerate(clue):
        for new_chr in clue_chr_possibilities:
            if new_chr != clue_chr:
                new_clue = clue[:i] + new_chr + clue[i + 1:]
                new_clues.append(new_clue)

    new_solution_spaces = []
    for new_clue in new_clues:
        try:
            new_solution_space = _update(solution_space, guess, new_clue)
        except IncompatibleClueError:
            continue
        new_solution_spaces.append(new_solution_space)

    return new_solution_spaces


def _update(solution_space: SolutionSpace, guess: str, clue: str) -> SolutionSpace:
    new_solution_space = copy.deepcopy(solution_space)
    a = ord('a')
    print("clue: ", clue)
    for i, (guess_chr, clue_chr) in enumerate(zip(guess, clue)):
        guess_chr_idx: int = ord(guess_chr) - a

        if clue_chr == 'Y':
            if new_solution_space.possible[i][guess_chr_idx] == 0:
                raise IncompatibleClueError()
            if new_solution_space.confirmed[i] is not None and new_solution_space.confirmed[i] != guess_chr:
                raise IncompatibleClueError()

            for j in range(26):
                if j != guess_chr_idx:
                    new_solution_space.possible[i][j] = 0

            new_solution_space.confirmed[i] = guess_chr

        elif clue_chr == 'X':
            # We cannot rule out the letter entirely if it appears elsewhere in the guess with a clue of '~' or 'Y'
            squiggly_appears = False
            for j, c in enumerate(guess):
                if c == guess_chr and clue[j] == '~':
                    squiggly_appears = True
            for j in range(5):
                if (not squiggly_appears and not (guess[j] == guess_chr and clue[j] == 'Y')) or j == i:
                    new_solution_space.possible[j][guess_chr_idx] = 0

        else: # If the clue was "~"
            if all(new_solution_space.possible[j][guess_chr_idx] == 0 for j in range(5)):
                raise IncompatibleClueError()
            if new_solution_space.confirmed[i] == guess_chr:
                raise IncompatibleClueError()

            # No space for the character to go anywhere else in the word
            num_non_nones_in_confirmed = sum(1 for c in new_solution_space.confirmed if c is not None)
            has_space_for_chr = False
            if num_non_nones_in_confirmed >= 4:
                for j in range(5):
                    if j != i and new_solution_space.confirmed[j] is None:
                        has_space_for_chr = True
            if not has_space_for_chr:
                raise IncompatibleClueError()
    print("new solution space: ", new_solution_space.__str__())
    return new_solution_space