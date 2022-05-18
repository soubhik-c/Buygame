from typing import Iterable

import pygame

from common.gameconstants import TILE_ADJ_MULTIPLIER, INIT_TILE_SIZE, Align, Colors, BG_COLOR
from common.gamesurvey import PreGQs
from gui.button import InputText, RadioButton
from gui.gui_common.display import Display
from gui.gui_common.fontmixin import FontMixin
from gui.label import Label
from gui.survey.survey_question import SurveyQuestion


class SurveyInput(SurveyQuestion):
    class Page(FontMixin):
        def __init__(self, parent):
            super().__init__()
            self.p = parent
            self.controls = []
            self.tile_sz = Display.TILE_SIZE
            self.cur_x = 5 * self.tile_sz
            self.cur_y = 2 * self.tile_sz
            self.font_sz = 18
            self.font_nm = "comicsans"

        def add_input(self, label: PreGQs, txt_sz):
            _txt = InputText(self.cur_x, self.cur_y,
                             label.q,
                             "",
                             max_length=txt_sz)
            self.controls.append(_txt)
            self.cur_y += _txt.height()

        def add_options(self, label: PreGQs, opts: [str]):
            self.cur_y += self.tile_sz
            lbl = Label(self.cur_x//self.tile_sz, self.cur_y//self.tile_sz, 5, 2,
                        align=Align.LEFT,
                        font_sz=self.font_sz, font_nm=self.font_nm, italic=False)
            lbl.set_text(label.q)
            self.cur_y += lbl.height
            f = pygame.font.SysFont(self.font_nm, self.font_sz)
            rw = max([f.render(o, True, Colors.BLACK.value).get_width() for o in opts])//self.tile_sz
            rh = len(opts) - .5
            r = RadioButton(self.cur_x//self.tile_sz,
                            self.cur_y//self.tile_sz,
                            rw * TILE_ADJ_MULTIPLIER,
                            rh * TILE_ADJ_MULTIPLIER,
                            font_nm=self.font_nm,
                            font_sz=self.font_sz,
                            fill_color=BG_COLOR,
                            border_color=BG_COLOR,
                            on_display=True)
            [r.add_option(t) for t in opts]
            self.controls.append((lbl, r))
            self.cur_y += r.height + self.tile_sz

        def switch_to_right_column(self):
            self.cur_x += 29 * self.tile_sz
            self.cur_y = 2 * self.tile_sz

        def add_line_break(self, lines=1):
            self.cur_y += (lines * self.tile_sz)

        def draw(self, surface):
            for c in self.controls:
                if isinstance(c, Iterable):
                    [_ic.draw(surface) for _ic in c]
                else:
                    c.draw(surface)

    def __init__(self):
        super(SurveyInput, self).__init__()
        self.pages = []
        self.cur_pg = 0

    def new_page(self) -> Page:
        p = SurveyInput.Page(self)
        self.pages.append(p)
        return p

    def _cur_pg(self):
        return self.pages[self.cur_pg]

    def draw(self, surface):
        self._cur_pg().draw(surface)

    def has_next(self):
        return self.cur_pg < (len(self.pages)-1)

    def move_next(self):
        self.cur_pg += 1

    def has_prev(self):
        return self.cur_pg > 0

    def move_prev(self):
        self.cur_pg -= 1
