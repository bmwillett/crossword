from tqdm import tqdm
import pickle
import os

import logging
log = logging.getLogger("crossword_logger")

CANDIDATES_PATH = os.path.dirname(os.path.abspath(__file__)) + '/../data/candidates/'


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
        to be implemented in child classes

        input: dictionary 'entry' with keys:

        'cell': (integer) index of cell in grid
        'AD': (string) in ['A', 'D']: whether clue is across or down
        'length': (integer) length of word
        'clue': (string) text string of clue

        returns list of candidate words, ordered from most to least likely
        """
        raise NotImplementedError




