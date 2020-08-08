"""
Solving algorithms:

BACKTRACKING ALGORITHM:

for each clue, generate a list of n likely choices.  now the goal is to find a global solution which minimizes the number of entries not coming from these likely choices
more specifically, let us try to find a solution that uses all but k of these (ie, up to k entries from the grid are unconstrained, the others all come from the n suggestions)
we write an algorithm A_k, below, that tries to find such a solution for a given k, or else indicates that one does not exist
then we will iterate through k, starting at zero, and find the first k for which a solution exists, and return that grid as our solution

algorithm A_k:
    - initialize stack with:
    [ (empty grid, entry_idx_to_try = 0, cand_idx_to_try = 0)]
    - while stack is non-empty:
        - pop from stack
        - go through possible entries, starting with entry_idx_to_try, cand_idx_to_try:
            - see if fits in grid
            - if fits in grid, see how many mistakes (must be <=k)
        - if passes, add original grid and new grid back to queue and repeat
    either find complete solution or stack is empty => no solution for this k

PRIORITY QUEUE ALGORITHM:

 TODO: implement this, if necessary

"""

import puz
from heapq import heappop, heappush
from collections import defaultdict
import logging
import os

from clue_solvers import Oracle, WebSolver

logging.basicConfig()
log = logging.getLogger("crossword_logger")
log.setLevel(logging.INFO)

PUZ_DIR = './data/puzzles/'
EXAMPLE_PUZ = 'Jul0220'
EXAMPLE_PUZ = 'mgwcc636'
MAX_EXCLUDED = 50
MAX_ITERS = 50000
PRINT_FREQ = 10000

class Grid:
    def __init__(self, grid, remaining_candidates, num_excluded=0):
        """
        :param grid: partially complete crossword grid (list of list of chars)

        :param remaining_candidates:  candidates to try next, stored in the format:
        [ (entry_idx_1, [cand_idx_1, ...]), ...]

        where entry_idx_i is the index in entries, and cand_idx_i is the index in candidates[entry_idx_i]

        Note: elements to try next appear at the end of lists, so that they may be popped

        :param num_excluded: number of entries in the grid where no candidates remain
        """
        self.grid = [[c for c in row] for row in grid]
        self.remaining_candidates = {entry_idx: [cand_idx for cand_idx in remaining_candidates[entry_idx]]
                                     for entry_idx in remaining_candidates}
        self.num_excluded = num_excluded

        # determine candidate order
        self.candidates_to_try = [entry_idx for _, entry_idx in sorted(
            [(len(self.remaining_candidates[entry_idx]), entry_idx) for entry_idx in self.remaining_candidates],
            reverse=True)]

        self.width, self.height = len(grid[0]), len(grid)

    def get_entry(self, cell, AD):
        r, c = cell // self.width, cell % self.width
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

    def place(self, word, entry_idx, entries, candidates, crossings):
        """
        tries to place 'word' in grid at location 'cell'
        checks:
         - word fits in grid
         - does not cause more than MAX_EXCLUDED errors

        returns new Grid object with placed word if successful, else None
        """

        cell, AD, length, _ = entries[entry_idx].values()

        log.debug(f"trying to fit {word} in cell {cell}")

        # check if word fits in grid
        slot = self.get_entry(cell, AD)
        if len(word) != len(slot) or any([c1 != c2 and c2 != '-' for c1, c2 in zip(word, slot)]):
            log.debug("doesn't fit in space -> invalid entry")
            return None
        log.debug("fits in space!")

        # make copies of parameters to create new Grid object
        new_remaining_candidates = {_entry_idx: [cand_idx for cand_idx in self.remaining_candidates[_entry_idx]]
                                    for _entry_idx in self.remaining_candidates}
        del new_remaining_candidates[entry_idx]
        new_num_excluded = self.num_excluded

        # check crossings to see what candidates are eliminated
        for (_entry_idx, pos), c in zip(crossings, word):
            new_entry_candidates = []
            for cand_idx in new_remaining_candidates.get(_entry_idx, []):
                if candidates[_entry_idx][cand_idx][pos] == c:
                    new_entry_candidates.append(cand_idx)
            if len(new_entry_candidates) > 0:
                new_remaining_candidates[_entry_idx] = new_entry_candidates
            else:
                if _entry_idx in new_remaining_candidates:
                    del new_remaining_candidates[_entry_idx]
                    new_num_excluded += 1

        if new_num_excluded > MAX_EXCLUDED:
            log.debug("too many excluded -> invalid entry!")
            return None
        log.debug("found valid entry!")

        # valid entry, create new Grid object
        new_grid = [[c for c in row] for row in self.grid]
        r, c = cell // self.width, cell % self.width
        for i in range(len(word)):
            new_grid[r][c] = word[i]
            if AD == 'A':
                c += 1
            else:
                r += 1

        if log.level == logging.DEBUG:
            log.debug("new grid:")
            self.print()

        newGrid = Grid(new_grid, new_remaining_candidates, new_num_excluded)
        return newGrid

    @property
    def is_filled(self):
        return all([all([x != '-' for x in row]) for row in self.grid])

    def print(self):
        print("\ngrid:")
        print('_'*(2*self.width+1))
        for row in self.grid:
            line = ['|']
            for c in row:
                if c == '-':
                    line.append(' ')
                elif c == '.':
                    line.append('■')
                else:
                    line.append(c.upper())
                line.append(' ')
            line[-1] = '|'
            print(''.join(line))
        print('‾'*(2*self.width+1) + '\n')
        print("current num_exlcuded = ", self.num_excluded)


def get_intersections(entries, grid):
    width, height = len(grid[0]), len(grid)
    cells = [{} for _ in range(width * height)]

    intersections = []
    for idx, entry in enumerate(entries):
        (cell, AD, length, _) = entry.values()
        intersections.append([() for _ in range(length)])
        gap = 1 if AD == 'A' else width
        for i in range(length):
            cells[cell + i * gap][idx] = i

    for cell in cells:
        if not cell:
            continue
        [idx1, idx2] = cell.keys()
        [i1, i2] = cell.values()
        intersections[idx1][i1] = (idx2, i2)
        intersections[idx2][i2] = (idx1, i1)

    return intersections


def solve_puz(puz_name, clue_model=None, load_candidates=True, save_candidates=False):

    p = puz.read(PUZ_DIR + puz_name + '.puz')

    numbering = p.clue_numbering()
    initial_grid = [[c for c in numbering.grid[i * p.width:(i + 1) * p.width]] for i in range(p.height)]

    entries = []

    for elem in numbering.across:
        cell, length, clue = elem['cell'], elem['len'], elem['clue'].lower()
        entries.append({'cell': cell, 'AD': 'A', 'length': length, 'clue': clue})

    for elem in numbering.down:
        cell, length, clue = elem['cell'], elem['len'], elem['clue'].lower()
        entries.append({'cell': cell, 'AD': 'D', 'length': length, 'clue': clue})

    intersections = get_intersections(entries, initial_grid)

    if clue_model is None:
        clue_model = Oracle(p, entries, puz_name, load=load_candidates, save=save_candidates)
    elif clue_model == 'web':
        clue_model = WebSolver(entries, puz_name, load=load_candidates, save=save_candidates)

    initial_remaining_candidates = {idx: list(range(len(clue_model.candidates[idx])))[::-1]
                                    for idx in clue_model.candidates}

    # backtracking solution
    stack = [Grid(initial_grid, initial_remaining_candidates)]

    # TODO:
    #  - modify algorithm so we try most constrained clues first
    #  - test if works fast enough (was very slow before)
    #  - then try to get working with websolver (after fixing VPN issue)
    #  - if working, test on Gaffneys
    #  - finally, go back and work more on BERT model

    iters = 0
    while stack:
        grid = stack.pop()
        found_next = False

        if iters > MAX_ITERS:
            return grid, clue_model
        if iters % PRINT_FREQ == 0:
            grid.print()
        iters += 1

        while grid.candidates_to_try:
            entry_idx = grid.candidates_to_try.pop()
            cand_idx_list = grid.remaining_candidates[entry_idx]
            cell, AD, length, _ = entries[entry_idx].values()
            crossings = intersections[entry_idx]

            while cand_idx_list:
                cand_idx = cand_idx_list.pop()
                candidate_word = clue_model.candidates[entry_idx][cand_idx]

                new_grid = grid.place(candidate_word, entry_idx, entries, clue_model.candidates, crossings)
                if new_grid:
                    if new_grid.is_filled:
                        return new_grid, clue_model
                    grid.entry_idx_to_try, grid.cand_idx_to_try = entry_idx, cand_idx + 1
                    stack.append(grid)
                    stack.append(new_grid)
                    found_next = True
                    break

            if found_next:
                break
    return None


if __name__ == '__main__':
    sol, clue_model = solve_puz(EXAMPLE_PUZ, clue_model="web")

    import IPython; IPython.embed(); exit(1)
