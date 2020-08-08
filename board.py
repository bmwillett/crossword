import logging
import puz
import pygame as pg
from tkinter import filedialog
import tkinter as tk
import os
import shutil

from solver import solve_puz

logging.basicConfig()
log = logging.getLogger("TR_logger")
log.setLevel(logging.DEBUG)

PUZ_DIR = './data/puzzles/'

def open_file():
    # Make a top-level instance and hide since it is ugly and big.
    root = tk.Tk()
    root.withdraw()

    # Make it almost invisible - no decorations, 0 size, top left corner.
    root.overrideredirect(True)
    root.geometry('0x0+0+0')

    # Show window again and lift it to top so it can get focus,
    # otherwise dialogs will end up behind the terminal.
    root.deiconify()
    root.lift()
    root.focus_force()

    filename = filedialog.askopenfilename(parent=root)  # Or some other dialog

    # Get rid of the top-level instance once to make it actually invisible.
    root.destroy()

    return filename

fname = open_file()

pg.init()
screen = pg.display.set_mode((900, 950))

COLOR_INACTIVE = pg.Color('white')
COLOR_ACTIVE = pg.Color('yellow')
COLOR_TEXT = pg.Color('black')
COLOR_BORDER = pg.Color('black')
COLOR_SELECT = pg.Color('red')
COLOR_CLUE_BG = pg.Color('gray')

FONT = pg.font.Font(None, 32)
CLUE_NUM_FONT = pg.font.Font(None, 16)

CLUE_HEIGHT = 50

class Board:
    def __init__(self, w, h, p, board=None):
        self.input_boxes = []
        self.rows, self.cols = p.height, p.width
        self.board_w, self.board_h = w, h-CLUE_HEIGHT

        global FONT
        FONT = pg.font.Font(None, int(0.9 * self.board_w / self.cols))

        numbering = p.clue_numbering()
        self.across_cells = {cell_dat['cell']: (cell_dat['num'], cell_dat['clue']) for cell_dat in numbering.across}
        self.down_cells = {cell_dat['cell']:  (cell_dat['num'], cell_dat['clue'])for cell_dat in numbering.down}

        self.board = [[p.fill[r * p.width + c] for c in range(p.width)] for r in range(p.height)] if board is None else board
        self.sel_across = True
        self.active_word_cell = None

        # handle clue
        self.current_clue = ''
        self.clue_bg = pg.Rect(0, 0, self.board_w, CLUE_HEIGHT)
        self.clue_text = FONT.render(self.current_clue, True, COLOR_TEXT)
        self.clues = {cell: self.across_cells[cell][0] for cell in self.across_cells}
        self.clues.update({cell: self.down_cells[cell][0] for cell in self.down_cells})

        # create boxes in grid
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != '.':
                    self.input_boxes.append(InputBox(int(self.board_w * c / self.cols),
                                                     CLUE_HEIGHT + int(self.board_h * r / self.rows),
                                                     int(self.board_w / self.cols),
                                                     int(self.board_h / self.rows)))
                    if len(self.input_boxes)-1 in self.clues:
                        self.input_boxes[-1].clue_num = str(self.clues[len(self.input_boxes)-1])
                    if board[r][c] != '-':
                        self.input_boxes[-1].text = board[r][c].upper()
                        self.input_boxes[-1].txt_surface = FONT.render(board[r][c].upper(), True, COLOR_TEXT)

                else:
                    self.input_boxes.append(NullBox())

        self.active_r, self.active_c = None, None

    def handle_event(self, event):
        if event.type != pg.MOUSEBUTTONDOWN and event.type != pg.KEYDOWN:
            return

        self.active_r, self.active_c = None, None
        just_entered_letter = False
        for i, box in enumerate(self.input_boxes):
            box.inactiveword = False
            box.handle_event(event)
            if box.active:
                self.active_r, self.active_c = i // self.cols, i % self.cols
                if box.just_entered_letter:
                    box.just_entered_letter = False
                    just_entered_letter = True

        if just_entered_letter:
            self.input_boxes[self.cols * self.active_r + self.active_c].active = False
            if self.sel_across:
                self.shift_active(0, 1)
            else:
                self.shift_active(1, 0)


        if event.type == pg.KEYDOWN and self.active_c is not None:
            self.input_boxes[self.cols * self.active_r + self.active_c].active = False
            if event.key == pg.K_LEFT:
                if self.sel_across:
                    self.shift_active(0, -1)
                self.sel_across =  True
            if event.key == pg.K_RIGHT:
                if self.sel_across:
                    self.shift_active(0, 1)
                self.sel_across = True
            if event.key == pg.K_UP:
                if not self.sel_across:
                    self.shift_active(-1, 0)
                self.sel_across = False
            if event.key == pg.K_DOWN:
                if not self.sel_across:
                    self.shift_active(1, 0)
                self.sel_across = False
            if event.key == pg.K_TAB:
                self.sel_across = not self.sel_across
            if event.key == pg.K_BACKSPACE:
                if self.sel_across:
                    self.shift_active(0, -1)
                else:
                    self.shift_active(-1, 0)

            self.input_boxes[self.cols * self.active_r + self.active_c].active = True

        self.update_active_word()


    def shift_active(self, dr, dc):
        self.active_r += dr
        self.active_c += dc
        if not(0 <= self.active_r < self.rows and 0 <= self.active_c < self.cols):
            self.active_r -= dr
            self.active_c -= dc
            return False
        if self.board[self.active_r][self.active_c] == '.':
            if not self.shift_active(dr, dc):
                self.active_r -= dr
                self.active_c -= dc
                return False
        return True

    def update_active_word(self):
        if self.active_c is None:
            self.current_clue = ''
            return

        def update(r, c, dr, dc):
            while 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] != '.':
                self.input_boxes[self.cols * r + c].inactiveword = True
                self.active_word_cell = r * self.cols + c
                r += dr
                c += dc

        if self.sel_across:
            update(self.active_r, self.active_c, 0, 1)
            update(self.active_r, self.active_c, 0, -1)
        else:
            update(self.active_r, self.active_c, 1, 0)
            update(self.active_r, self.active_c, -1, 0)

        clue = self.across_cells[self.active_word_cell] if self.sel_across \
                                else self.down_cells[self.active_word_cell]
        self.current_clue = str(clue[0]) + '. ' + clue[1]

    def draw(self, screen):
        for box in self.input_boxes:
            box.draw(screen)
        self.draw_clue()

    def draw_clue(self):
        # TODO: format longer clues correctly
        self.clue_text = FONT.render(self.current_clue, True, COLOR_TEXT)
        pg.draw.rect(screen, COLOR_CLUE_BG, self.clue_bg, 0)
        screen.blit(self.clue_text, (5, 5))


class NullBox:
    def __init__(self):
        self.active = False
        self.inactiveword = False

    def handle_event(self, event):
        pass

    def draw(self, screen):
        pass

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.w, self.h = w, h
        self.rect = pg.Rect(x, y, w, h)
        self.sel_rect = pg.Rect(x, y, w-2, h-2)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, COLOR_TEXT)
        self.active = False
        self.inactiveword = False
        self.just_entered_letter = False
        self.clue_num = ''

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_BACKSPACE:
                    self.text = ''
                else:
                    text_input = event.unicode.upper()
                    if text_input.isalpha():
                        self.text = event.unicode.upper()
                        self.just_entered_letter = True
                    # TODO
                    # - make sure its a letter
                    # - shift focus to appropriate square
                    # - handle across/down focus
                    # - later - allow rebus

                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, COLOR_TEXT)

    def draw(self, screen):
        # Blit the rects and text
        self.color = COLOR_ACTIVE if self.inactiveword else COLOR_INACTIVE
        pg.draw.rect(screen, self.color, self.rect, 0)
        if self.text != '':
            txt_w, txt_h = self.txt_surface.get_rect().w, self.txt_surface.get_rect().h
            offset_x, offset_y = (self.w-txt_w)//2, (self.h-txt_h)//2
            screen.blit(self.txt_surface, (self.rect.x + offset_x, self.rect.y + offset_y))
        if self.clue_num != '':
            screen.blit(CLUE_NUM_FONT.render(self.clue_num, True, COLOR_TEXT), (self.rect.x + 3, self.rect.y + 3))
        pg.draw.rect(screen, COLOR_BORDER, self.rect, 1)
        if self.active:
            pg.draw.rect(screen, COLOR_SELECT, self.sel_rect, 4)


def main(filename):

    puz_name = os.path.basename(fname)[:-4]
    if os.path.realpath(filename[:-(len(puz_name)+4)]) != os.path.realpath(PUZ_DIR):
        # save copy of puzzle in puzzle directory
        with open(fname, 'rb') as fr:
            with open (PUZ_DIR + puz_name + '.puz', 'wb') as fw:
                shutil.copyfileobj(fr, fw)

    # generate (partial) solution
    sol, clue_model = solve_puz(puz_name, clue_model="web")

    # load crossword data
    p = puz.read(filename)
    pg.display.set_caption('"' + p.title + '" ' + p.author)

    # set up screen
    w, h = pg.display.get_surface().get_size()
    board = Board(w, h, p, board=sol.grid)

    clock = pg.time.Clock()
    done = False

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            board.handle_event(event)

        screen.fill(COLOR_BORDER)
        board.draw(screen)

        pg.display.flip()
        clock.tick(30)

    import IPython; IPython.embed(); exit(1)


if __name__ == '__main__':
    main(fname)
    pg.quit()
