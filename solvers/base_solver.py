from collections import defaultdict
import sys

import logging
log = logging.getLogger("crossword_logger")

from clue_models import OracleSolver, WebSolver
from solvers.grid_state import GridState


class Solver:
    def __init__(self, clue_model_type='oracle', load_candidates=True, save_candidates=False, puz_name=''):
        self.clue_model_type = clue_model_type
        self.load_candidates = load_candidates
        self.save_candidates = save_candidates
        self.puz_name = puz_name

    def solve_puz(self, p):
        numbering = p.clue_numbering()
        initial_grid = [[c for c in numbering.grid[i * p.width:(i + 1) * p.width]] for i in range(p.height)]

        entries = []

        for elem in numbering.across:
            cell, length, clue = elem['cell'], elem['len'], elem['clue'].lower()
            entries.append({'cell': cell, 'AD': 'A', 'length': length, 'clue': clue})

        for elem in numbering.down:
            cell, length, clue = elem['cell'], elem['len'], elem['clue'].lower()
            entries.append({'cell': cell, 'AD': 'D', 'length': length, 'clue': clue})

        if self.clue_model_type == 'oracle':
            self.clue_model = OracleSolver(p, entries, self.puz_name, load=self.load_candidates, save=self.save_candidates)
        elif self.clue_model_type == 'web':
            self.clue_model = WebSolver(entries, self.puz_name, load=self.load_candidates, save=self.save_candidates)
        else:
            raise NotImplementedError(f"Clue model {self.clue_model_type} not implemented")

        entry_cells = [(e['AD'], e['cell'] // p.width, e['cell'] % p.width) for e in entries]
        all_candidates = {entry: cands for entry, cands in  zip(entry_cells, self.clue_model.candidates.values())}

        initial_remaining_candidates = {entry: list(range(len(all_candidates[entry])))[::-1]
                                        for entry in entry_cells}

        # make crossings
        cells = [[] for _ in range(p.width * p.height)]
        for idx, entry in enumerate(entries):
            (cell, AD, length, _) = entry.values()
            gap = 1 if AD == 'A' else p.width
            for i in range(length):
                cells[cell + i * gap].append((idx, i))
        crossings = defaultdict(list)
        for cell in cells:
            if not cell:
                continue
            [[idx1, i1], [idx2, i2]] = cell
            crossings[entry_cells[idx1]].append((entry_cells[idx2], i1, i2))
            crossings[entry_cells[idx2]].append((entry_cells[idx1], i2, i1))

        initial_board_state = GridState(initial_grid, initial_remaining_candidates, all_candidates, crossings, num_excluded=0, num_empty=None)

        return self._solver(initial_board_state), self.clue_model

    def _solver(self):
        """
        solving method, must be implemented in child class
        """
        raise NotImplementedError
