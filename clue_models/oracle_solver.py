import string

import logging
log = logging.getLogger("crossword_logger")

from clue_models.base_clue_solver import ClueSolver

ALPHABET = list(string.ascii_lowercase)


class OracleSolver(ClueSolver):
    """
    assumes puz file comes with solution, so correct answer for each clue is known
    depending on mode, can return candidate list containing correct answer and/or several wrong answers
    used for testing solver
    """
    MODEL_NAME = 'oracle'

    def __init__(self, p, entries, puzname, num_candidates_per_entry=None, load=True, save=False):
        super().__init__(num_candidates_per_entry=num_candidates_per_entry, load=load, save=save)

        self.solution = p.solution
        self.width = p.width

        # read off correct answers from puz file
        self.answers = {}
        for entry in p.clue_numbering().across:
            cell, length = entry['cell'], entry['len']
            self.answers[(cell, 'A')] = ''.join([self.solution[cell + i] for i in range(length)]).lower()

        for entry in p.clue_numbering().down:
            cell, length = entry['cell'], entry['len']
            self.answers[(cell, 'D')] = ''.join([self.solution[cell + i*self.width] for i in range(length)]).lower()

        self.generate_candidates(entries, puzname)

    def find_clue(self, entry, mode='correct_plus_random_from_grid'):
        cell, AD, length, _ = tuple(entry.values())

        answer = self.answers[(cell, AD)]
        if mode == 'correct_only':
            return [answer]
        elif mode == 'correct_plus_random_letters':
            # returns correct answer plus a string of random letters, in random order
            out = [answer]
            for i in range(self.num_candidates_per_entry - 1):
                out.append(''.join(np.random.choice(ALPHABET, length)))
            np.random.shuffle(out)
            return out
        elif mode == 'correct_plus_random_from_grid':
            # returns correct answer plus a random other entries from grid
            out = [answer]
            same_length_words = [word for word in self.answers.values() if len(word) == length]
            out.extend(list(np.random.choice(same_length_words, self.num_candidates_per_entry - 1)))
            np.random.shuffle(out)
            return out


if __name__ == '__main__':
    log.setLevel(logging.DEBUG)
    logging.basicConfig()

    model = OracleSolver()
    model({'clue': 'What are you?', 'length': 6})
