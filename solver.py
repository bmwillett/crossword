"""
Given a crossword (DECIDE FORMAT), and a model to produce candidate words (DECIDE FORMAT),
generate most likely solution

for each clue, the model presents a set of candidate answers with probabilities
then the algorithm tries to generate a globally consistent solution with the highest probabiliity

--------------------------------
EXAMPLE 2x2 crossword:

clue probabilities:
1A. {'aa': 0.9, 'ab': 0.1}
2A. {'ab': 0.9, 'bb': 0.1}
1D. {'aa': 0.9, 'ab': 0.1}
2D. {'bb': 0.9, 'ab': 0.1}

possible consistent solutions:

AA
BB

probability ~  0.9 * 0.1 * 0.1 * 0.1

AB
AB

probability ~ 0.1 * 0.9 * 0.9 * 0.9

-> second solution is preferred

-------------------------------

Solving algorithm ideas:

BACKTRACKING ALGORITHM:

for each clue, generate a list of n likely choices.  now the goal is to find a global solution which minimizes the number of entries not coming from these likely choices
more specifically, let us try to find a solution that uses all but k of these (ie, up to k entries from the grid are unconstrained, the others all come from the n suggestions)
we write an algorithm A_k, below, that tries to find such a solution for a given k, or else indicates that one does not exist
then we will iterate through k, starting at zero, and find the first k for which a solution exists, and return that grid as our solution

algorithm A_k:
    - initialize stack with:
    [ (empty grid, entry_idx_to_try = 0, candidate_idx_to_try = 0)]
    - while stack is non-empty:
        - pop from stack
        - go through possible entries, starting with entry_idx_to_try, candidate_idx_to_try:
            - see if fits in grid
            - if fits in grid, see how many mistakes (must be <=k)
        - if passes, add original grid and new grid back to queue and repeat
    either find complete solution or stack is empty => no solution for this k

PRIORITY QUEUE ALGORITHM:

 TODO: implement


"""

import puz
import numpy as np
from heapq import heappop, heappush
from collections import defaultdict
import logging
import string
from tqdm import tqdm

from clue_solvers import Oracle, WebSolver

logging.basicConfig()
log = logging.getLogger("crossword_logger")
log.setLevel(logging.DEBUG)

EXAMPLE_PUZ = './data/puzzles/Jul0120.puz'
ALPHABET = list(string.ascii_lowercase)


class Grid:
    k = 1

    def __init__(self, grid, candidates_left, num_missing=0):
        self.grid = [[c for c in row] for row in grid]
        self.candidates_left = [[x for x in row] for row in candidates_left]
        self.num_missing = num_missing

        self.width, self.height = len(grid[0]), len(grid)
        self.entry_idx_to_try = 0
        self.candidate_idx_to_try = 0

    def get_entry(self, cell, AD):
        r, c = cell//self.width, cell % self.width
        out = []
        if AD == 'A':
            while c < self.width and self.grid[r][c] != '.':
                out.append(self.grid[r][c])
                c += 1
        elif AD == 'D':
            while r < self.height and self.grid[r][c] != '.':
                out.append(self.grid[r][c])
                r += 1

        return ''.join(out)

    def place(self, word, cell, AD, crossings, candidates):
        """
        tries to place 'word' in grid at location 'cell'
        checks:
         - word fits in grid
         - does not cause more than self.k errors

        returns new Grid object with placed word if successful, else None
        """

        # check if word fits in grid
        slot = self.get_entry(cell, AD)

        # check if already filled
        if not any([c == '-' for c in slot]):
            return None

        log.debug(f"trying to fit {word} in cell {cell}")

        if len(word) != len(slot) or any([c1 != c2 and c2 != '-' for c1, c2 in zip(word, slot)]):
            log.debug("doesn't fit in space -> invalid entry")
            return None
        log.debug("fits in space!")

        # check crossings to see what candidates are eliminated
        new_candidates_left = [[x for x in row] for row in self.candidates_left]
        new_num_missing = self.num_missing

        for (entry_idx, pos), c in zip(crossings, word):
            for i, candidate in enumerate(candidates[entry_idx]):
                if candidate[pos] != c:
                    new_candidates_left[entry_idx][i] = False
            if any(self.candidates_left[entry_idx]) and not any(new_candidates_left[entry_idx]):
                new_num_missing += 1

        if new_num_missing > self.k:
            log.debug("too many wrong -> invalid entry!")
            return None
        log.debug("not too many wrong -> valid entry!")

        # valid entry, create new Grid object
        new_grid = [[c for c in row] for row in self.grid]
        r, c = cell//self.width, cell % self.width
        for i in range(len(word)):
            new_grid[r][c] = word[i]
            if AD == 'A':
                c += 1
            else:
                r += 1

        if log.level == logging.DEBUG:
            self.print()

        newGrid = Grid(new_grid, new_candidates_left, new_num_missing)
        return newGrid

    @property
    def is_filled(self):
        return all([all([x != '-' for x in row]) for row in self.grid])

    def print(self):
        print("\ngrid:")
        for row in self.grid:
            line = []
            for c in row:
                if c == '-':
                    line.append(' ')
                elif c == '.':
                    line.append('#')
                else:
                    line.append(c.upper())
            print(''.join(line))
        print("\n")


def get_intersections(entries, grid):
    width, height = len(grid[0]), len(grid)
    cells = [{} for _ in range(width*height)]

    intersections = []
    for idx, entry in enumerate(entries):
        (cell, AD, length, _) = entry.values()
        intersections.append([() for _ in range(length)])
        gap = 1 if AD == 'A' else width
        for i in range(length):
            cells[cell + i*gap][idx] = i

    for cell in cells:
        if not cell:
            continue
        [idx1, idx2] = cell.keys()
        [i1, i2] = cell.values()
        intersections[idx1][i1] = (idx2, i2)
        intersections[idx2][i2] = (idx1, i1)

    return intersections

def solve_puz(filename, clue_model=None):
    p = puz.read(filename)

    numbering = p.clue_numbering()
    initial_grid = [[c for c in numbering.grid[i*p.width:(i+1)*p.width]] for i in range(p.height)]

    entries = []

    for elem in numbering.across:
        cell, length, clue = elem['cell'], elem['len'], elem['clue'].lower()
        entries.append({'cell': cell, 'AD': 'A', 'length': length, 'clue': clue})

    for elem in numbering.down:
        cell, length, clue = elem['cell'], elem['len'], elem['clue'].lower()
        entries.append({'cell': cell, 'AD': 'D', 'length': length, 'clue': clue})

    intersections = get_intersections(entries, initial_grid)

    if clue_model is None:
        clue_model = Oracle(p)

    log.info("collecting candidates...")
    candidates = []
    for entry in tqdm(entries):
        candidates.append(clue_model(entry))

    candidates_left = [[True for _ in row] for row in candidates]


    import IPython; IPython.embed(); exit(1)

    # backtracking solution
    stack = [Grid(initial_grid, candidates_left)]

    while stack:
        grid = stack.pop()
        found_next = False
        entry_idx_to_try, candidate_idx_to_try = grid.entry_idx_to_try, grid.candidate_idx_to_try

        for entry_idx in range(entry_idx_to_try, len(entries)):
            entry_candidates = candidates[entry_idx]
            cell, AD, length, _ = entries[entry_idx].values()
            crossings = intersections[entry_idx]

            for candidate_idx in range(candidate_idx_to_try, len(entry_candidates)):
                new_grid = grid.place(entry_candidates[candidate_idx], cell, AD, crossings, candidates)
                if new_grid:
                    if new_grid.is_filled:
                        return new_grid
                    grid.entry_idx_to_try, grid.candidate_idx_to_try = entry_idx, candidate_idx + 1
                    stack.append(grid)
                    stack.append(new_grid)
                    found_next = True
                    break

            if found_next:
                break
    return None


if __name__ == '__main__':
    sol = solve_puz(EXAMPLE_PUZ, clue_model=WebSolver())
    import IPython; IPython.embed(); exit(1)