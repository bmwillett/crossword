"""
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

"""
import logging
log = logging.getLogger("crossword_logger")

from solvers.base_solver import Solver

MAX_ITERS = 100000
PRINT_FREQ = 10000

class BacktrackSolver(Solver):
    def _solver(self, initial_grid_state):

        # backtracking solution
        stack = [initial_grid_state]

        iters = 0
        while stack:
            grid = stack.pop()
            found_next = False

            if iters > MAX_ITERS:
                return grid
            if iters % PRINT_FREQ == 0:
                grid.print()
            iters += 1

            while grid.candidates_to_try:
                entry = grid.candidates_to_try.pop()
                cand_idx_list = grid.remaining_candidates[entry]
                crossings = grid.crossings[entry]

                while cand_idx_list:
                    cand_idx = cand_idx_list.pop()
                    candidate_word = grid.all_candidates[entry][cand_idx]

                    new_grid = grid.place(candidate_word, entry)
                    if new_grid:
                        if new_grid.is_filled:
                            return new_grid
                        # grid.entry_idx_to_try, grid.cand_idx_to_try = entry_idx, cand_idx + 1
                        stack.append(grid)
                        stack.append(new_grid)
                        found_next = True
                        break

                if found_next:
                    break
        return None


if __name__ == '__main__':
    import puz

    logging.basicConfig()
    log.setLevel(logging.DEBUG)

    PUZ_DIR = '../data/puzzles/'
    EXAMPLE_PUZ = ['Jul0220', 'mgwcc636'][1]
    MAX_EXCLUDED = 40
    PRINT_FREQ = 10000
    MAX_ITERS = 500000

    p = puz.read(PUZ_DIR + EXAMPLE_PUZ + '.puz')
    solver = BacktrackSolver(clue_model="web", puz_name=EXAMPLE_PUZ)

    sol, clue_model = solver.solve_puz(p)
    print("found solution!")
    sol.print()

    import IPython; IPython.embed(); exit(1)