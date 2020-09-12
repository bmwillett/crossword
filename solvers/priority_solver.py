import logging
log = logging.getLogger("crossword_logger")


from solvers.priority_search import QueueState, PrioritySearch
from solvers.base_solver import Solver

class CrosswordQueueState(QueueState):
    def __init__(self, grid_state):
        self.grid_state = grid_state

    def _moves(self):
        for entry in self.grid_state.candidates_to_try:
            for cand_idx in self.grid_state.remaining_candidates[entry]:
                word = self.grid_state.all_candidates[entry][cand_idx]
                new_state = self.grid_state.place(word, entry)
                if new_state is not None:
                    yield CrosswordQueueState(new_state)

    def _heuristic(self):
        # TODO: test following idea:
        #  value of state = number of entered leters minus number of clues with no valid candidate words left
        #  pros: if solution exists among candidate words, this will be maximized on it
        #  cons: not sure what happens if not, or if guarantees the fastest path to solution
        EXCLUDED_WEIGHT = 2
        return self.grid_state.num_empty + EXCLUDED_WEIGHT * self.grid_state.num_excluded

    def _done(self):
        return self.grid_state.is_filled

    def print(self):
        self.grid_state.print()
        print("current value = ", self.heuristic, '\n')

    def __hash__(self):
        return tuple([tuple(row) for row in self.grid_state.grid]).__hash__()

class PrioritySolver(Solver):
    def _solver(self, initial_grid_state):
        initial_cqs = CrosswordQueueState(initial_grid_state)
        sol = PrioritySearch().search(initial_cqs)
        print("best value:", sol.heuristic)
        return sol.grid_state


if __name__ == '__main__':
    import puz

    logging.basicConfig()
    log.setLevel(logging.DEBUG)

    PUZ_DIR = '../data/puzzles/'
    EXAMPLE_PUZ = ['Jul0220', 'mgwcc636'][1]
    p = puz.read(PUZ_DIR + EXAMPLE_PUZ + '.puz')
    solver = PrioritySolver(clue_model="web", puz_name=EXAMPLE_PUZ)
    #solver = PrioritySolver(puz_name=EXAMPLE_PUZ)


    sol, clue_model = solver.solve_puz(p)
    print("found solution!")
    sol.print()

    import IPython; IPython.embed(); exit(1)