from heapq import heappush, heappop
import logging
log = logging.getLogger("crossword_logger")

PRINT_FREQ = 1000
MAX_ITERS = 25000

"""
base class for state used in priority search
"""
class QueueState:

    @property
    def moves(self):
        return self._moves()

    def _moves(self):
        """
        implement in child class:
        returns iterator running over all states that can be obtained from the given state
        """
        pass

    @property
    def heuristic(self):
        return self._heuristic()

    def _heuristic(self):
        """
        implement in child class:
        returns heuristic function evaluating current state, used in priority search
        """
        pass

    @property
    def done(self):
        return self._done()

    def _done(self):
        """
        implement in child class:
        returns boolean indicating that this is a final state, used to terminate search
        """
        pass

    def print(self):
        """
        optional: print state for debugging purposes
        """
        pass

    def __lt__(self, other):
        return self.heuristic < other.heuristic

    def __hash__(self):
        """
        must implement hash function for saving visited states
        """
        raise NotImplementedError


# searches for shortest path on given grid, used to test priority search class
class PathSearchState(QueueState):
    def __init__(self, grid, path, target):
        self.grid = grid
        self.path = path
        self.pos = path[-1]
        self.target = target

    def _moves(self):
        moves = [(self.pos[0] + i, self.pos[1]+j) for (i,j) in [(1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1)]]
        for (i,j) in moves:
            if i < 0 or i >= self.grid.shape[0] or j < 0 or j >= self.grid.shape[1]:
                continue
            if (i,j) in self.path:
                continue
            new_path = self.path + [(i,j)]
            yield PathSearchState(self.grid, new_path, self.target)

    def _heuristic(self):
        return sum([self.grid[i][j] for (i,j) in self.path])

    def _done(self):
        return self.pos == self.target

    def __hash__(self):
        return tuple(self.path).__hash__()

    def __repr__(self):
        return f"PathSearchState(path = {self.path}, cost={self.heuristic})"

class StateIterator:
    NUM_CANDS_SAVED = 10

    def __init__(self, state):
        self.state = state
        self.idx = 0
        self.cur_candidates =[]
        try:
            self.next_candidate = self._get_next()
            self.has_next = True
        except:
            self.next_candidate = None
            self.has_next = False

    def get_next(self):
        """
        return next candidate, retrieves the one after that and stores in self.next_candidate
        """
        next_candidate = self.next_candidate
        try:
            self.next_candidate = self._get_next()
        except:
            self.has_next = False
            self.next_candidate = None
        return next_candidate

    def _get_next(self):
        """
        maintains list of next self.NUM_CANDS_SAVED candidates
        after this runs out, generates all candidates and selects next sequence
        avoids storing entire candidate list in memory, but at cost of recomputing (hopefully not too often)
        """
        if self.idx % self.NUM_CANDS_SAVED == 0:
            all_candidates = self._generate_candidates()
            self.cur_candidates = all_candidates[self.idx:self.idx + self.NUM_CANDS_SAVED]
        self.idx += 1
        return self.cur_candidates[(self.idx - 1) % self.NUM_CANDS_SAVED]

    def _generate_candidates(self):
        """
        generates a list of all possible states that can reached from this state, in order of decreasing heuristic
        """
        candidates = []

        for state in self.state.moves:
            candidates.append(state)

        return sorted(candidates)

    def __lt__(self, other):
        if self.next_candidate is None:
            return True
        if other.next_candidate is None:
            return False
        return self.next_candidate < other.next_candidate


class PrioritySearch:

    def search(self, initial_state):
        """
        - put initial state in heap
        - while queue not empty:
            - pop state
            - get its best next state
            - see if already visited, if not put in queue
            - see if original state has other moves to try, if so put back in queue
            - continue until final state found

        """

        initial_state_iterator = StateIterator(initial_state)
        queue = [initial_state_iterator]
        visited = {initial_state}
        best_so_far = initial_state
        iters = 0

        while queue:
            cur_state_iterator = heappop(queue)
            next_state = cur_state_iterator.get_next()

            if next_state.done:
                return next_state

            if next_state not in visited:
                visited.add(next_state)
                next_state_iterator = StateIterator(next_state)
                if next_state_iterator.has_next:
                    heappush(queue, next_state_iterator)

            if cur_state_iterator.has_next:
                heappush(queue, cur_state_iterator)

            if next_state < best_so_far:
                best_so_far = next_state
            if iters % PRINT_FREQ == 0 and log.level == logging.DEBUG:
                next_state.print()
                print(f"iteration: {iters}/{MAX_ITERS}")
            if iters > MAX_ITERS:
                return best_so_far
            iters += 1

        return best_so_far

def grid_search_test():

    import numpy as np

    grid = np.array(
        [[1, 1, 1, 1, 1, 1],
         [1, 1, 9, 9, 1, 1],
         [1, 1, 9, 1, 1, 1],
         [1, 1, 9, 1, 1, 1],
         [1, 1, 9, 1, 1, 1]])

    start = (4,1)
    target = (2,3)
    initial_grid_state = PathSearchState(grid, [start], target)

    priority_search = PrioritySearch()
    shortest_path = priority_search.search(initial_grid_state)

    print("Found path!")
    print(shortest_path)
    print(grid)

if __name__ == '__main__':
    grid_search_test()
