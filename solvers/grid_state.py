import logging
log = logging.getLogger("crossword_logger")

class GridState:
    def __init__(self, grid, remaining_candidates, all_candidates, crossings, num_excluded=0, num_empty=None):

        # grid state data
        self.grid = [[c for c in row] for row in grid] # make copy of grid

        self.remaining_candidates = {entry: [cand_idx for cand_idx in remaining_candidates[entry]]
                                     for entry in remaining_candidates} # make copy of remaining candidates
        self.num_excluded = num_excluded
        if num_empty is None:
            num_empty = sum([len([c for c in row if c == '-']) for row in grid])
        self.num_empty = num_empty

        # global grid information
        self.all_candidates = all_candidates
        self.crossings = crossings

        # determine optimal candidate order (for backtracking)
        self.candidates_to_try = [entry for _, entry in sorted(
            [(len(self.remaining_candidates[entry]), entry) for entry in self.remaining_candidates],
            reverse=True)]

        self.width, self.height = len(grid[0]), len(grid)

    def get_entry(self, entry):
        AD, r, c = entry
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

    def place(self, word, entry):
        (AD, r, c) = entry
        #log.debug(f"trying to fit {word} in cell {(r,c)}")

        cur_word = self.get_entry(entry)
        if not(len(word) == len(cur_word) and all([c1 == c2 or c2 == '-' for c1, c2 in zip(word, cur_word)])):
            return None

        # make copies of parameters to create new Grid object
        new_remaining_candidates = {_entry: [cand_idx for cand_idx in self.remaining_candidates[_entry]]
                                    for _entry in self.remaining_candidates}
        del new_remaining_candidates[entry]
        new_num_excluded = self.num_excluded
        new_num_empty = self.num_empty

        # check crossings to see what candidates are eliminated
        for _entry, i1, i2 in self.crossings[entry]:
            l = word[i1]
            new_entry_candidates = []
            for cand_idx in new_remaining_candidates.get(_entry, []):
                if self.all_candidates[_entry][cand_idx][i2] == l:
                    new_entry_candidates.append(cand_idx)
            if len(new_entry_candidates) > 0:
                new_remaining_candidates[_entry] = new_entry_candidates
            elif _entry in new_remaining_candidates:
                del new_remaining_candidates[_entry]
                new_num_excluded += 1

        # valid entry, create new Grid object
        new_grid = [[c for c in row] for row in self.grid]
        for i in range(len(word)):
            if new_grid[r][c] == '-':
                new_num_empty -= 1
            new_grid[r][c] = word[i]
            if AD == 'A':
                c += 1
            else:
                r += 1

        return GridState(new_grid, new_remaining_candidates, self.all_candidates, self.crossings, num_excluded=new_num_excluded, num_empty=new_num_empty)

    @property
    def is_filled(self):
        return self.num_empty == 0

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
#        print("current num_exlcuded = ", self.num_excluded)
