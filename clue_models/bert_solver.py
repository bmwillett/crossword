import logging
log = logging.getLogger("crossword_logger")

from clue_models.base_clue_solver import ClueSolver


class BERTSolver(ClueSolver):
    """
    solver based on BERT model
    model defined in 'clue_net.py'
    """
    MODEL_NAME = 'bert'

    def __init__(self):
        super().__init__()
        self.model = None
        # TODO: create and train (or load pretrained) Bert model and add here

