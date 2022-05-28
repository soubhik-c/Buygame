from typing import Iterable

import pygame

from common.gameconstants import TILE_ADJ_MULTIPLIER, INIT_TILE_SIZE, Align, Colors, BG_COLOR
from common.gamesurvey import PreGQs, GameSurveyQs
from gui.button import InputText, RadioButton
from gui.gui_common.display import Display
from gui.gui_common.fontmixin import FontMixin
from gui.label import Label
from gui.survey.survey_question import SurveyQuestion


class SurveyInput(SurveyQuestion):
    class Page(FontMixin):
        def __init__(self, parent, surface):
            super().__init__()
            self.p = parent
            self.surface = surface
            self.controls = []
            self.tile_sz = Display.TILE_SIZE
            self.cur_x = 5 * self.tile_sz
            self.cur_y = 2 * self.tile_sz
            self.font_sz = 18
            self.font_nm = "comicsans"

        def add_input(self, sq: PreGQs, txt_sz, in_focus=False):
            _txt = InputText(self.surface, self.font,
                             self.cur_x, self.cur_y,
                             sq.q,
                             "",
                             in_focus=in_focus,
                             max_length=txt_sz)
            self.controls.append((sq, None, _txt))
            self.cur_y += _txt.height()

        def add_options(self, sq: PreGQs, opts: [str]):
            self.cur_y += self.tile_sz
            lbl = Label(self.cur_x // self.tile_sz, self.cur_y // self.tile_sz, 5, 2,
                        align=Align.LEFT,
                        font_sz=self.font_sz, font_nm=self.font_nm, italic=False)
            lbl.set_text(sq.q)
            self.cur_y += lbl.height
            f = pygame.font.SysFont(self.font_nm, self.font_sz)
            rw = max([f.render(o, True, Colors.BLACK.value).get_width() for o in opts]) // self.tile_sz
            rh = len(opts)
            r = RadioButton(self.cur_x // self.tile_sz,
                            self.cur_y // self.tile_sz,
                            rw * TILE_ADJ_MULTIPLIER,
                            rh * TILE_ADJ_MULTIPLIER,
                            font_nm=self.font_nm,
                            font_sz=self.font_sz,
                            fill_color=BG_COLOR,
                            border_color=BG_COLOR,
                            on_display=True)
            [r.add_option(t) for t in opts]
            self.controls.append((sq, lbl, r))
            self.cur_y += r.height + self.tile_sz

        def switch_to_right_column(self):
            self.cur_x += 29 * self.tile_sz
            self.cur_y = 2 * self.tile_sz

        def add_line_break(self, lines=1):
            self.cur_y += (lines * self.tile_sz)

        def foreach(self, fn):
            for c in self.controls:
                if isinstance(c, Iterable):
                    [fn(_ic) for _ic in c]
                else:
                    fn(c)

        def draw(self, surface):
            def dr(_c):
                if _c is not None and not isinstance(_c, GameSurveyQs):
                    _c.draw(surface)
            self.foreach(dr)

        def in_focus(self):
            self.foreach(lambda _c: _c.show() if isinstance(_c, InputText) else None)

        def out_focus(self):
            self.foreach(lambda _c: _c.hide() if isinstance(_c, InputText) else None)

        def mouse_down(self, mouse):
            self.foreach(lambda _c: _c.click(*mouse) if isinstance(_c, RadioButton) else None)

        def mouse_up(self, mouse):
            self.foreach(lambda _c: _c.click(*mouse) if isinstance(_c, RadioButton) else None)

        def get_result(self) -> [(GameSurveyQs, str)]:
            res: [(GameSurveyQs, str)] = []
            for c in self.controls:
                sq, _, _e = c
                assert isinstance(sq, GameSurveyQs)
                if isinstance(_e, InputText):
                    _e.end_input()
                    res.append((sq, f"\"{_e.text}\""))
                elif isinstance(_e, RadioButton):
                    res.append((sq, f"\"{_e.get_chosen_option_str()}\""))
            return res

    def __init__(self):
        super(SurveyInput, self).__init__()
        self.pages = []
        self.cur_pg = 0

    def new_page(self, surface) -> Page:
        p = SurveyInput.Page(self, surface)
        self.pages.append(p)
        return p

    def _cur_pg(self):
        return self.pages[self.cur_pg]

    def draw(self, surface):
        self._cur_pg().draw(surface)

    def has_next(self):
        return self.cur_pg < (len(self.pages) - 1)

    def move_next(self):
        self._cur_pg().out_focus()
        self.cur_pg += 1
        self._cur_pg().in_focus()

    def has_prev(self):
        return self.cur_pg > 0

    def move_prev(self):
        self.cur_pg -= 1

    def mouse_down(self, mouse):
        self._cur_pg().mouse_down(mouse)

    def mouse_up(self, mouse):
        self._cur_pg().mouse_up(mouse)

    def get_result(self) -> [(GameSurveyQs, str)]:
        res: [(GameSurveyQs, str)] = []
        [res.append(e) for _p in self.pages for e in _p.get_result()]
        return res
