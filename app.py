import puz
import pygame as pg
from collections import namedtuple
import os
import shutil

import logging
log = logging.getLogger("crossword_logger")

logging.basicConfig()
log.setLevel(logging.DEBUG)

from utils.utils import open_file
from solvers import BacktrackSolver, PrioritySolver
from utils.board_gui import BoardGUI

DisplayData = namedtuple('DisplayData', ['CLUE_HEIGHT',
                                       'COLOR_INACTIVE',
                                       'COLOR_ACTIVE',
                                       'COLOR_TEXT',
                                       'COLOR_BORDER',
                                       'COLOR_SELECT',
                                       'COLOR_CLUE_BG',
                                       'GRID_FONT',
                                       'CLUE_FONT',
                                       'CLUE_NUM_FONT'])

PUZ_DIR = './data/puzzles/'

def main(get_solution=True):

    # load puz file
    fname = open_file()
    puz_name = os.path.basename(fname)[:-4]
    if os.path.realpath(fname[:-(len(puz_name)+4)]) != os.path.realpath(PUZ_DIR):
        # save copy of puzzle in puzzle directory
        with open(fname, 'rb') as fr:
            with open (PUZ_DIR + puz_name + '.puz', 'wb') as fw:
                shutil.copyfileobj(fr, fw)
    p = puz.read(fname)

    # TODO: implement pop up window to select clue and solve models

    # generate (partial) solution
    if get_solution:
        # use backtrack or priority solver
        solver = [BacktrackSolver(clue_model_type="web", puz_name=puz_name),
                  PrioritySolver(clue_model_type="web", puz_name=puz_name)][1]

        sol, clue_model = solver.solve_puz(p)
        print("\nsolution:")
        board = sol.grid
        candidates = clue_model.candidates
    else:
        board, candidates = None, None

    # initialize board gui based on pygame
    pg.init()
    board_data = DisplayData(CLUE_HEIGHT = 30,
                             COLOR_INACTIVE = pg.Color('white'),
                             COLOR_ACTIVE = pg.Color('yellow'),
                             COLOR_TEXT = pg.Color('black'),
                             COLOR_BORDER = pg.Color('black'),
                             COLOR_SELECT = pg.Color('red'),
                             COLOR_CLUE_BG = pg.Color('gray'),
                             GRID_FONT = pg.font.Font(None, 50),
                             CLUE_FONT = pg.font.Font(None, 30),
                             CLUE_NUM_FONT = pg.font.Font(None, 16))
    screen = pg.display.set_mode((900, 900 + 2 * board_data.CLUE_HEIGHT))
    pg.display.set_caption('"' + p.title + '" ' + p.author)
    board = BoardGUI(screen, p, board=board, candidates=candidates, board_data=board_data)

    clock = pg.time.Clock()
    done = False

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            board.handle_event(event)

        screen.fill(board_data.COLOR_BORDER)
        board.draw(screen)

        pg.display.flip()
        clock.tick(30)

    pg.quit()


if __name__ == '__main__':
    main(get_solution=True)
