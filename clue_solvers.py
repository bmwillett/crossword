import urllib.parse
import requests
import re
import logging

log = logging.getLogger("crossword_logger")

class ClueSolver:
    """
    base class of clue solver
    """
    def __init__(self):
        pass

    def __call__(self, entry):
        self.find_clue(entry)

    def find_clue(self):
        """
        input: dictionary 'entry' with keys:

        'cell': (integer) index of cell in grid
        'AD': (string) in ['A', 'D']: whether clue is across or down
        'length': (integer) length of word
        'clue': (string) text string of clue

        returns list of candidate words, ordered from most to least likely
        """
        return []



class Oracle(ClueSolver):
    """
    assumes puz file comes with solution, so correct answer for each clue is known
    depending on mode, can return candidate list containing correct answer and/or several wrong answers
    used for testing solver
    """

    NUM_EXTRA = 6

    def __init__(self, p):
        super().__init__()

        self.solution = p.solution
        self.width = p.width
        self.answers = {}

        for entry in p.clue_numbering().across:
            cell, length = entry['cell'], entry['len']
            self.answers[(cell, 'A')] = ''.join([self.solution[cell + i] for i in range(length)]).lower()

        for entry in p.clue_numbering().down:
            cell, length = entry['cell'], entry['len']
            self.answers[(cell, 'D')] = ''.join([self.solution[cell + i*self.width] for i in range(length)]).lower()

    def find_clue(self, entry, mode='correct_only'):
        cell, AD, length, _ = entry
        gap = 1 if AD == 'A' else self.width

        answer = self.answers[(cell, AD)]
        if mode == 'correct_only':
            return [answer]
        elif mode == 'correct_plus_random_letters':
            # returns correct answer plus a string of random letters, in random order
            out = [answer]
            for i in range(self.NUM_EXTRA):
                out.append(''.join(np.random.choice(ALPHABET, length)))
            np.random.shuffle(out)
            return out
        elif mode == 'correct_plus_random_from_grid':
            # returns correct answer plus a random other entries from grid
            out = [answer]
            same_length_words = [word for word in self.answers.values() if len(word) == length]
            out.extend(list(np.random.choice(same_length_words, self.NUM_EXTRA)))
            np.random.shuffle(out)
            return out

class WebSolver(ClueSolver):
    """
    searches website 'wordplays.com' for clue
    collects top k results
    """
    DEFAULT_NUM_CANDIDATES = 5
    BASE_URL = 'https://www.wordplays.com/crossword-solver/'

    def __init__(self, num_candidates=None):
        super().__init__()
        self.num_candidates = self.DEFAULT_NUM_CANDIDATES if num_candidates is None else num_candidates

    def find_clue(self, entry):
        log.debug(f"\nlooking for answer for clue: {entry['clue']}")

        clue = urllib.parse.quote(entry['clue'])
        url = self.BASE_URL + clue
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5'})
        text = r.text

        # TODO: got banned from wordplays.com!
        #  -> try to use VPN

        out = []
        for s in re.finditer('<a href="/crossword-clues/', text):
            i = s.end()
            word = []
            while text[i] != '"':
                word.append(text[i])
                i += 1
            out.append(''.join(word).lower())
            if len(out) == self.num_candidates:
                break
        log.debug(f"found candidates: {out}")
        return out


class BERTModel(ClueSolver):
    """
    solver based on BERT model
    model defined in 'clue_model.py'
    """

    def __init__(self):
        super().__init__()
        self.model = None #create and train (or load pretrained) Bert model

if __name__ == '__main__':
    log.setLevel(logging.DEBUG)
    logging.basicConfig()

    model = WebSolver()
    model({'clue':'What are you?'})



