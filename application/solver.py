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
    # letters that are confirmed to be in the word, although their exact position might be unknown. This is a
    # superset of `confirmed`. Does not currently support knowing about there being multiple of the same letter
    # in the word.
    confirmed_position_agnostic: set[str]

    def __str__(self):
        possible_chrs = [[chr(ord('a') + j) for j in range(26) if (self.possible[i][j] == 1)] for i in range(5)]
        return (f"Possible characters: {possible_chrs}\n"
                f"Confirmed characters: {self.confirmed}"
                f"Confirmed position-agnostic characters: {self.confirmed_position_agnostic}")

    def is_word_compatible(self, word: str) -> bool:
        assert len(word) == 5, f"Word {word} must be 5 characters long"
        compatible = True
        for i, c in enumerate(word):
            if self.confirmed[i] is not None and self.confirmed[i] != c:
                compatible = False
                break

            idx = ord(c) - ord('a')
            if self.possible[i][idx] == 0:
                compatible = False
                break
        for c in self.confirmed_position_agnostic:
            if c not in word:
                compatible = False
                break
        return compatible


class IncompatibleClueError(Exception):
    pass


def initialize_solution_space(known_chr: str) -> SolutionSpace:
    return SolutionSpace(
        possible=[[1 for _ in range(26)] for _ in range(5)],
        confirmed=[None for _ in range(5)],
        confirmed_position_agnostic={known_chr},
    )


class Solver:
    def __init__(self, word_list: list[str], initial_solution_space: SolutionSpace):
        self.word_list = word_list
        self.solution_spaces = [initial_solution_space]

    def _get_potential_words_for_branch(self, solution_space: SolutionSpace) -> list[str]:
        return [word for word in self.word_list if solution_space.is_word_compatible(word)]

    def _get_potential_words_for_all_branches(self, solution_spaces: list[SolutionSpace]) -> set[str]:
        return {
            word
            for solution_space in solution_spaces
            for word in self._get_potential_words_for_branch(solution_space)
        }

    def pick_guess(self) -> str:
        compatible_words = list(self._get_potential_words_for_all_branches(self.solution_spaces))
        compatible_words.sort()
        print("Compatible words: ", compatible_words)
        print("Number of compatible words: ", len(compatible_words))
        if not compatible_words:
            raise Exception("No compatible words found")
        return compatible_words[0]

    def expand_solution_spaces(
            self,
            guess: str, clue: str,
            fact_or_fiction_check: Optional[tuple[int, bool]]
    ) -> None:
        new_solution_spaces = []
        for solution_space in self.solution_spaces:
            new_solution_spaces += self.expand_solution_space(solution_space, guess, clue, fact_or_fiction_check)
        self.solution_spaces = new_solution_spaces
        print("Number of solution space branches: ", len(self.solution_spaces))

    # Given the current solution space, a guess and a clue that contains exactly 1 lie, returns a
    # list of solution space branches, where each branch supposes that the lie is in a different
    # position in the clue.
    @classmethod
    def expand_solution_space(
            cls,
            solution_space: SolutionSpace,
            guess: str,
            clue: str,
            fact_or_fiction_check: Optional[tuple[int, bool]]
    ) -> list[SolutionSpace]:
        # Generate all possible correct clues, given a clue with a single lie.
        clue_chr_possibilities = ['Y', 'X', '~']
        new_clues = []

        if fact_or_fiction_check:
            position, is_fact = fact_or_fiction_check
            if not is_fact: # Every other position must be the truth. The lie is at `position`.
                for new_chr in clue_chr_possibilities:
                    if new_chr != clue[position]:
                        new_clue = clue[:position] + new_chr + clue[position + 1:]
                        new_clues.append(new_clue)
            else: # There is no lie at `position`
                for i, clue_chr in enumerate(clue):
                    if i == position:
                        continue
                    for new_chr in clue_chr_possibilities:
                        if new_chr != clue_chr:
                            new_clue = clue[:i] + new_chr + clue[i + 1:]
                            new_clues.append(new_clue)
        else:
            for i, clue_chr in enumerate(clue):
                for new_chr in clue_chr_possibilities:
                    if new_chr != clue_chr:
                        new_clue = clue[:i] + new_chr + clue[i + 1:]
                        new_clues.append(new_clue)

        new_solution_spaces = []
        for new_clue in new_clues:
            try:
                new_solution_space = cls._update(solution_space, guess, new_clue)
            except IncompatibleClueError:
                continue
            new_solution_spaces.append(new_solution_space)

        return new_solution_spaces

    @classmethod
    def _update(cls, solution_space: SolutionSpace, guess: str, clue: str) -> SolutionSpace:
        new_solution_space = copy.deepcopy(solution_space)
        a = ord('a')
        for i, (guess_chr, clue_chr) in enumerate(zip(guess, clue)):
            guess_chr_idx: int = ord(guess_chr) - a

            if clue_chr == 'Y':
                if new_solution_space.possible[i][guess_chr_idx] == 0:
                    raise IncompatibleClueError()
                if new_solution_space.confirmed[i] and new_solution_space.confirmed[i] != guess_chr:
                    raise IncompatibleClueError()
                if (len(new_solution_space.confirmed_position_agnostic) >= 5
                        and guess_chr not in new_solution_space.confirmed_position_agnostic):
                    raise IncompatibleClueError()

                for j in range(26):
                    if j != guess_chr_idx:
                        new_solution_space.possible[i][j] = 0

                new_solution_space.confirmed[i] = guess_chr
                new_solution_space.confirmed_position_agnostic.add(guess_chr)

            elif clue_chr == 'X':
                # We cannot rule out the letter entirely if it appears elsewhere in the guess with a clue of '~' or 'Y'
                squiggly_appears = False
                for j, c in enumerate(guess):
                    if c == guess_chr and clue[j] == '~':
                        squiggly_appears = True
                for j in range(5):
                    if (not squiggly_appears and not (guess[j] == guess_chr and clue[j] == 'Y')) or j == i:
                        new_solution_space.possible[j][guess_chr_idx] = 0

            else:  # If the clue was "~"
                if all(new_solution_space.possible[j][guess_chr_idx] == 0 for j in range(5)):
                    raise IncompatibleClueError()
                if new_solution_space.confirmed[i] == guess_chr:
                    raise IncompatibleClueError()
                if (len(new_solution_space.confirmed_position_agnostic) >= 5
                        and guess_chr not in new_solution_space.confirmed_position_agnostic):
                    raise IncompatibleClueError()

                # Check if there is space for the character to go anywhere else in the word
                has_space_for_chr = False
                for j in range(5):
                    if (j != i and new_solution_space.confirmed[j] is None
                            and new_solution_space.possible[j][guess_chr_idx] == 1):
                        has_space_for_chr = True
                if not has_space_for_chr:
                    raise IncompatibleClueError()

                new_solution_space.possible[i][guess_chr_idx] = 0
                new_solution_space.confirmed_position_agnostic.add(guess_chr)
        return new_solution_space
