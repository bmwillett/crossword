import urllib.parse
import requests
import re
import logging
import numpy as np
import time
import string
from tqdm import tqdm
import pickle
import os

log = logging.getLogger("crossword_logger")

ALPHABET = list(string.ascii_lowercase)
CANDIDATES_PATH = './data/candidates/'

class ClueSolver:
    """
    base class of clue solver
    """

    DEFAULT_NUM_CANDIDATES_PER_ENTRY = 5
    MODEL_NAME = 'base'
    ERROR = 'ERROR'

    def __init__(self, num_candidates_per_entry=None, load=True, save=False):
        self.num_candidates_per_entry = self.DEFAULT_NUM_CANDIDATES_PER_ENTRY if num_candidates_per_entry is None else num_candidates_per_entry
        self.load = load
        self.save = save
        self.candidates = {}

    def generate_candidates(self, entries, puzname):
        self.candidates = {}
        cand_file_path = CANDIDATES_PATH + puzname + '_' + self.MODEL_NAME

        if self.load and os.path.exists(cand_file_path):
            log.info("loading candidates...")
            with open(cand_file_path, 'rb') as f:
                self.candidates = pickle.load(f)

        log.debug(f"got here with candidates = {self.candidates}")
        log.info("creating candidates...")
        for idx, entry in tqdm(enumerate(entries)):
            if not self.load or idx not in self.candidates or type(self.candidates[idx]) is not list:
                self.candidates[idx] = self.find_clue(entry)
                self.save = True # force save if updating any elements TODO: better way?
        if self.save:
            log.info("saving candidates...")
            with open(cand_file_path, 'wb') as f:
                pickle.dump(self.candidates, f, pickle.HIGHEST_PROTOCOL)

        # finally, replace all errors by empty lists, so algorithm will run
        for idx in self.candidates:
            if self.candidates[idx] == self.ERROR:
                self.candidates[idx] = []

    def __call__(self, entry):
        return self.find_clue(entry)

    def find_clue(self, entry):
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

class WebSolver(ClueSolver):
    """
    searches website 'wordplays.com' for clue
    collects top k results
    """
    MODEL_NAME = 'web'

    BASE_URL = 'https://www.wordplays.com/crossword-solver/'
    USE_PROXY = False
    PROXIES = {'http': 'socks5://user:pass@host:port',
               'https': 'socks5://user:pass@host:port'} if USE_PROXY else {}
    TIMEOUT = 5
    SLEEP_TIME = 2
    SEARCH_STRING = '<a href="/crossword-clues/'
    GOT_BANNED = '<!DOCTYPE html>\n<html lang="" prefix="og: http://ogp.me/ns#" >\n<head>\n<title>Contact Wordplays.com'

    def __init__(self, entries, puzname, num_candidates_per_entry=None, load=True, save=True):
        super().__init__(num_candidates_per_entry=num_candidates_per_entry, load=load, save=save)
        self.banned = False
        self.generate_candidates(entries, puzname)

    def find_clue(self, entry):
        if self.banned:
            return self.ERROR

        log.info(f"\nlooking for answer for clue: {entry['clue']}")

        length = entry['length']
        clue = urllib.parse.quote(entry['clue'])
        url = self.BASE_URL + clue
        try:
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5'}, proxies=self.PROXIES, timeout=self.TIMEOUT)
        except:
            log.info("connection error!  probably got banned!")
            self.banned = True
            return self.ERROR

        text = r.text
        if r.text.startswith(self.GOT_BANNED):
            log.info("got banned!")
            self.banned = True
            return self.ERROR

        out = []
        for s in re.finditer(self.SEARCH_STRING, text):
            i = s.end()
            word = []
            while text[i] != '"':
                word.append(text[i])
                i += 1
            if len(word) != length:
                continue
            out.append(''.join(word).lower())
            if len(out) == self.num_candidates_per_entry:
                break
        log.info(f"found candidates: {out}")

        time.sleep(self.SLEEP_TIME)
        return out

class BERTModel(ClueSolver):
    """
    solver based on BERT model
    model defined in 'clue_model.py'
    """
    MODEL_NAME = 'bert'

    def __init__(self):
        super().__init__()
        self.model = None
        # TODO: create and train (or load pretrained) Bert model and add here

if __name__ == '__main__':
    log.setLevel(logging.DEBUG)
    logging.basicConfig()

    model = WebSolver()
    model({'clue': 'What are you?', 'length': 6})



