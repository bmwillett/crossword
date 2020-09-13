import pygame as pg

class BoardGUI:
    def __init__(self, screen, p, board=None, candidates=None, board_data=None):

        # get display data
        self.board_data = board_data
        w, h = screen.get_size()

        # get board information
        self.board_w, self.board_h = w, h - 2*self.board_data.CLUE_HEIGHT
        self.rows, self.cols = p.height, p.width
        self.board = [[p.fill[r * p.width + c] for c in range(p.width)] for r in range(p.height)] if board is None else board

        # get clue information
        numbering = p.clue_numbering()
        candidates = list(candidates.values())[::-1] if candidates is not None else ['']*(len(numbering.across) + len(numbering.down))
        self.across_cells = {cell_dat['cell']: (cell_dat['num'], cell_dat['clue'], f'CANDIDATES: {candidates.pop()}') for cell_dat in numbering.across}
        self.down_cells = {cell_dat['cell']:  (cell_dat['num'], cell_dat['clue'], f'CANDIDATES: {candidates.pop()}')for cell_dat in numbering.down}

        # handle clue and candidates
        self.current_clue = ''
        self.current_candidates = ''
        self.clue_bg = pg.Rect(0, 0, self.board_w, self.board_data.CLUE_HEIGHT)
        self.candidate_bg = pg.Rect(0, self.board_data.CLUE_HEIGHT, self.board_w, self.board_data.CLUE_HEIGHT)
        self.clue_text = self.board_data.CLUE_FONT.render(self.current_clue, True, self.board_data.COLOR_TEXT)
        self.candidate_text = self.board_data.CLUE_FONT.render(self.current_candidates, True, self.board_data.COLOR_TEXT)
        self.clues = {cell: self.across_cells[cell][0] for cell in self.across_cells}
        self.clues.update({cell: self.down_cells[cell][0] for cell in self.down_cells})

        # create boxes in grid
        self.input_boxes = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != '.':
                    self.input_boxes.append(InputBox(int(self.board_w * c / self.cols),
                                                     2*self.board_data.CLUE_HEIGHT + int(self.board_h * r / self.rows),
                                                     int(self.board_w / self.cols),
                                                     int(self.board_h / self.rows),
                                                     board_data=self.board_data))
                    if len(self.input_boxes)-1 in self.clues:
                        self.input_boxes[-1].clue_num = str(self.clues[len(self.input_boxes)-1])
                    if self.board[r][c] != '-':
                        self.input_boxes[-1].text = self.board[r][c].upper()
                        self.input_boxes[-1].txt_surface = self.board_data.GRID_FONT.render(self.board[r][c].upper(), True, self.board_data.COLOR_TEXT)
                else:
                    self.input_boxes.append(NullBox())

        # entry selection
        self.sel_across = True
        self.active_word_cell = None
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
                    self.board[i // self.rows][i % self.cols] = box.text

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
        self.current_candidates = clue[2]

    def draw(self, screen):
        for box in self.input_boxes:
            box.draw(screen)
        self.draw_clue(screen)

    def draw_clue(self, screen):
        # TODO: format longer clues correctly
        self.clue_text = self.board_data.CLUE_FONT.render(self.current_clue, True, self.board_data.COLOR_TEXT)
        pg.draw.rect(screen, self.board_data.COLOR_CLUE_BG, self.clue_bg, 0)
        screen.blit(self.clue_text, (5, 5))
        self.candidate_text = self.board_data.CLUE_FONT.render(self.current_candidates, True, self.board_data.COLOR_TEXT)
        pg.draw.rect(screen, self.board_data.COLOR_CLUE_BG, self.candidate_bg, 0)
        screen.blit(self.candidate_text, (5, self.board_data.CLUE_HEIGHT + 5))


class NullBox:
    def __init__(self):
        self.active = False
        self.inactiveword = False

    def handle_event(self, event):
        pass

    def draw(self, screen):
        pass

class InputBox:
    def __init__(self, x, y, w, h, board_data, text=''):
        self.w, self.h = w, h
        self.rect = pg.Rect(x, y, w, h)
        self.sel_rect = pg.Rect(x, y, w-2, h-2)

        self.board_data = board_data
        self.color = board_data.COLOR_INACTIVE
        self.font = board_data.GRID_FONT

        self.text = text
        self.txt_surface = self.font.render(text, True, board_data.COLOR_TEXT)
        self.clue_num = ''

        self.active = False
        self.inactiveword = False
        self.just_entered_letter = False


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
                self.txt_surface = self.font.render(self.text, True, self.board_data.COLOR_TEXT)

    def draw(self, screen):
        # Blit the rects and text
        self.color = self.board_data.COLOR_ACTIVE if self.inactiveword else self.board_data.COLOR_INACTIVE
        pg.draw.rect(screen, self.color, self.rect, 0)
        if self.text != '':
            txt_w, txt_h = self.txt_surface.get_rect().w, self.txt_surface.get_rect().h
            offset_x, offset_y = (self.w-txt_w)//2, (self.h-txt_h)//2
            screen.blit(self.txt_surface, (self.rect.x + offset_x, self.rect.y + offset_y))
        if self.clue_num != '':
            screen.blit(self.board_data.CLUE_NUM_FONT.render(self.clue_num, True, self.board_data.COLOR_TEXT), (self.rect.x + 3, self.rect.y + 3))
        pg.draw.rect(screen, self.board_data.COLOR_BORDER, self.rect, 1)
        if self.active:
            pg.draw.rect(screen, self.board_data.COLOR_SELECT, self.sel_rect, 4)

