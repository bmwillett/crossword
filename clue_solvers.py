import urllib.parse
import requests
import re
import logging
import numpy as np
import time

log = logging.getLogger("crossword_logger")

USE_PROXY = False
PROXIES = {'http': 'socks5://user:pass@host:port',
           'https': 'socks5://user:pass@host:port'} if USE_PROXY else {}

SLEEP_TIME = 2
BAD_STRING = '<!DOCTYPE html>\n<html lang="" prefix="og: http://ogp.me/ns#" >\n<head>\n<title>Contact Wordplays.com'
CANDIDATE_PATH = './data/candidates/'

class ClueSolver:
    """
    base class of clue solver
    """

    DEFAULT_NUM_CANDIDATES_PER_ENTRY = 5

    def __init__(self, num_candidates_per_entry=None):
        self.num_candidates_per_entry = self.DEFAULT_NUM_CANDIDATES_PER_ENTRY if num_candidates_per_entry is None else num_candidates_per_entry

    def generate_candidates(self):
        # get candiates
        self.candidates = {}
        cand_file_path = CANDIDATE_PATH + puzname

        if load_candidates and os.path.exists(cand_file_path):
            log.info("loading candidates...")
            with open(cand_file_path, 'rb') as f:
                self.candidates = pickle.load(f)
        else:
            log.info("creating candidates...")
            for idx, entry in tqdm(enumerate(entries)):
                self.candidates[idx] = self(entry)
            if save_candidates:
                with open(cand_file_path, 'wb') as f:
                    pickle.dump(self.candidates, f, pickle.HIGHEST_PROTOCOL)

    def __call__(self, entry):
        return self.find_clue(entry)

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

    def __init__(self, p, entries, puzname, num_candidates_per_entry=None):
        super().__init__(num_candidates_per_entry=num_candidates_per_entry)

        self.solution = p.solution
        self.width = p.width
        self.answers = {}

        for entry in p.clue_numbering().across:
            cell, length = entry['cell'], entry['len']
            self.answers[(cell, 'A')] = ''.join([self.solution[cell + i] for i in range(length)]).lower()

        for entry in p.clue_numbering().down:
            cell, length = entry['cell'], entry['len']
            self.answers[(cell, 'D')] = ''.join([self.solution[cell + i*self.width] for i in range(length)]).lower()

    def find_clue(self, entry, mode='correct_plus_random_from_grid'):
        cell, AD, length, _ = tuple(entry.values())
        gap = 1 if AD == 'A' else self.width

        answer = self.answers[(cell, AD)]
        if mode == 'correct_only':
            return [answer]
        elif mode == 'correct_plus_random_letters':
            # returns correct answer plus a string of random letters, in random order
            out = [answer]
            for i in range(self.num_candidates - 1):
                out.append(''.join(np.random.choice(ALPHABET, length)))
            np.random.shuffle(out)
            return out
        elif mode == 'correct_plus_random_from_grid':
            # returns correct answer plus a random other entries from grid
            out = [answer]
            same_length_words = [word for word in self.answers.values() if len(word) == length]
            out.extend(list(np.random.choice(same_length_words, self.num_candidates - 1)))
            np.random.shuffle(out)
            return out

class WebSolver(ClueSolver):
    """
    searches website 'wordplays.com' for clue
    collects top k results
    """
    BASE_URL = 'https://www.wordplays.com/crossword-solver/'

    def __init__(self, num_candidates=None):
        super().__init__(num_candidates)
        self.banned = False

    def find_clue(self, entry):
        if self.banned:
            return 'BANNED'

        log.info(f"\nlooking for answer for clue: {entry['clue']}")

        length = entry['length']
        clue = urllib.parse.quote(entry['clue'])
        url = self.BASE_URL + clue
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5'}, proxies=PROXIES)
        text = r.text

        if r.text.startswith(BAD_STRING):
            self.banned = True
            return 'BANNED'

        out = []
        for s in re.finditer('<a href="/crossword-clues/', text):
            i = s.end()
            word = []
            while text[i] != '"':
                word.append(text[i])
                i += 1
            if len(word) != length:
                continue
            out.append(''.join(word).lower())
            if len(out) == self.num_candidates:
                break
        log.info(f"found candidates: {out}")

        time.sleep(SLEEP_TIME)
        return out


class BERTModel(ClueSolver):
    """
    solver based on BERT model
    model defined in 'clue_model.py'
    """

    def __init__(self):
        super().__init__()
        self.model = None
        # TODO: create and train (or load pretrained) Bert model and add here

if __name__ == '__main__':
    log.setLevel(logging.DEBUG)
    logging.basicConfig()

    model = WebSolver()
    model({'clue': 'What are you?', 'length': 6})



