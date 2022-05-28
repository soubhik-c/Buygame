import pygame
from pygame_widgets.textbox import TextBox

from common.gameconstants import Colors, TILE_ADJ_MULTIPLIER, NL_DELIM
from common.gamesurvey import GameSurveyQs, SURVEY_Qs_DELIM
from gui.gui_common.display import Display
from gui.gui_common.fontmixin import FontMixin
from gui.gui_common.subsurface import SubSurface
from gui.survey.survey_question import SurveyQuestion


class MultilineTextBox:
    def __init__(self, surface, x, y, width, height, lines, **kwargs):
        self.surface = surface
        self.line_texts: [TextBox] = []
        self.lt_pos = -1
        self.x, self.y = x, y
        self.w, self.h = width, height // lines
        self.lines = lines
        self.kwargs = kwargs
        self.kwargs["onSubmit"] = self.on_submit
        self.create_line = False
        self.offset = 5
        self.shdw = 7
        self.borderColour = [
            Colors.LTS_GRAY.value,
            Colors.LTR_GRAY.value,
            Colors.GRAY.value,
        ]
        self.borderWidth = [
            20,
            20,
            1,
        ]
        filloffset = self.offset + (self.shdw - self.offset) / 2
        self.borderRects = [
            pygame.Rect(self.x - self.shdw, self.y - self.shdw, width + self.shdw * 2, height + self.shdw * 2),
            pygame.Rect(self.x - filloffset, self.y - filloffset, width + filloffset * 2, height + filloffset * 2),
            pygame.Rect(self.x - self.offset, self.y - self.offset, width + self.offset * 2, height + self.offset * 2),
        ]
        self.selected = False

    def set_selected(self, lineno=0, _s=True):
        self.selected = _s
        b = self.line_texts[lineno]
        b.enable() if _s else b.disable()
        b.selected = b.showCursor = _s
        self.lt_pos = lineno if _s else self.lt_pos

    def add_new_line(self, num_actual_lines):
        for _ in range(num_actual_lines):
            yoffset = self.y + (len(self.line_texts) * (self.h + self.offset))
            t = TextBox(self.surface, self.x, yoffset, self.w, self.h, **self.kwargs)
            t.selected = t.showCursor = False
            t.cursorOffsetTop = 0
            t.textOffsetBottom = 0
            self.line_texts.append(t)

    def draw(self, _):
        for rect, color, bw in zip(self.borderRects, self.borderColour, self.borderWidth):
            pygame.draw.rect(self.surface, color, rect, width=1)

    def on_submit(self):
        pass
        # if len(self.line_texts) < 8 and not self.create_line:
        #     self.create_line = True

    def deselect(self):
        # disable every line
        [self.set_selected(lineno=i, _s=False) for i, _ in enumerate(self.line_texts)]

    def move_to_next_line(self, create_new=False):
        if self.lt_pos < len(self.line_texts) - 1 and \
                (create_new or len(self.line_texts[self.lt_pos + 1].text) > 0):
            self.set_selected(self.lt_pos, False)
            pygame.event.clear(pygame.KEYUP)
            self.lt_pos += 1
            self.set_selected(self.lt_pos, True)

    def move_to_prev_line(self):
        if self.lt_pos > 0:
            self.set_selected(self.lt_pos, False)
            pygame.event.clear(pygame.KEYUP)
            cur_pos = self.line_texts[self.lt_pos].cursorPosition
            self.lt_pos -= 1
            tb = self.line_texts[self.lt_pos]
            tb.cursorPosition = min(len(tb.text), cur_pos)
            self.set_selected(self.lt_pos, True)

    def has_max_length_reached(self):
        tb = self.line_texts[self.lt_pos]
        return tb.maxLengthReached and tb.cursorPosition == len(tb.text)

    def mouse_up(self, mouse):
        mx, my = mouse

        def is_line_clicked(_tb: TextBox):
            x, y = _tb.getX(), _tb.getY()
            return (x < mx < x + _tb.getWidth()) and \
                   (y < my < y + _tb.getHeight() + self.offset)

        if self.borderRects[0].collidepoint(*mouse):
            for i, tb in enumerate(self.line_texts):
                if is_line_clicked(tb):
                    self.set_selected(lineno=i, _s=True)
                    break
            return True

        return False

    def enable(self):
        for e in self.line_texts:
            e.enable()
            e.show()

    def disable(self):
        for e in self.line_texts:
            e.disable()
            e.hide()

    def get_text_str(self):
        return "\"" + "\n".join(["".join([_c for _c in _l.text]) for _l in self.line_texts]) + "\""

    def get_ser_text(self):
        return "\"" + \
               NL_DELIM.join(["".join([_c for _c in _l.text]).replace(NL_DELIM, '') for _l in self.line_texts]) + \
               "\""


class SurveyQuestionInputText(SurveyQuestion):
    class InputSection(FontMixin, Display):
        def __init__(self, parent, question: GameSurveyQs, max_input_len, h, v, w, ht):
            FontMixin.__init__(self)
            Display.__init__(self, h, v, w, ht)
            self.set_font_name("verdana")
            self.set_font_size(17)

            self.p = parent
            self.q = question
            self.ques = self.render_texts(self.q.q)
            self.tot_ques_font_ht = self.ques[0].get_height() * 1.1 * len(self.ques)
            self.mx_len = max_input_len
            self.text_box = MultilineTextBox(self.p.get_surface(),
                                             self.x,
                                             self.y,
                                             self.width,
                                             self.height,
                                             10,
                                             font=self.font,
                                             colour=Colors.WHITE.value,
                                             borderColour=Colors.LTR_GRAY.value,
                                             textColour=Colors.BLACK.value,
                                             radius=0, borderThickness=0)
            self.text_box.add_new_line(8)
            self.user_text = ""
            self.chars = 0
            self.enabled = False

        def set_input_selected(self, _s=True):
            self.text_box.set_selected(_s=_s)

        def enable(self):
            self.text_box.enable()
            self.enabled = True

        def disable(self):
            self.text_box.disable()
            self.enabled = False

        def draw(self, surface):
            if not self.enabled:
                return

            # font_pos = (self.x, self.y)
            tot_l = len(self.ques)
            per_row_ht = self.tot_ques_font_ht / len(self.ques)
            for i, qs in enumerate(self.ques, -1):
                surface.blit(qs, (self.x, self.y - ((tot_l - i) * per_row_ht)))
            self.text_box.draw(None)

        def str_result(self):
            return f"{self.q.__str__()}," + self.text_box.get_text_str()

        def get_user_inputs(self):
            return self.q, self.text_box.get_ser_text()

    def __init__(self, ssurface: SubSurface):
        super().__init__()
        self.ssurface = ssurface
        self.inputs: [SurveyQuestionInputText.InputSection] = []
        self.inputs_pos = -1
        # self.menu: Optional[thorpy.Menu] = None
        # self.thorpy_box = None

    def enable(self):
        [i.enable() for i in self.inputs]

    def disable(self):
        [i.disable() for i in self.inputs]

    def has_next(self):
        return False

    def has_prev(self):
        return False

    def draw(self, surface):
        [i.draw(surface) for i in self.inputs]

    def add_survey_question(self, ques: GameSurveyQs, max_input_len):
        block_sz = len(self.inputs) * (8 * TILE_ADJ_MULTIPLIER)
        self.inputs.append(
            SurveyQuestionInputText.InputSection(
                self, ques, max_input_len,
                8.5 * TILE_ADJ_MULTIPLIER,
                (3 * TILE_ADJ_MULTIPLIER) + block_sz,
                20 * TILE_ADJ_MULTIPLIER,
                5.5 * TILE_ADJ_MULTIPLIER
            ))

    def mouse_down(self, mouse):
        pass

    def mouse_up(self, mouse):
        [_in.text_box.deselect() for _in in self.inputs]
        for i, _in in enumerate(self.inputs):
            if _in.text_box.mouse_up(mouse):
                self.inputs_pos = i
                break

    def key_up(self, event: pygame.event.Event):
        if event.type == pygame.KEYUP:
            tb = self.inputs[self.inputs_pos].text_box
            if event.key == pygame.K_DOWN:
                tb.move_to_next_line()
            elif event.key == pygame.K_UP:
                tb.move_to_prev_line()
            elif event.key == pygame.K_TAB:
                pass
            elif event.key == pygame.K_RETURN:
                tb.move_to_next_line(create_new=True)
            elif tb.has_max_length_reached():
                tb.move_to_next_line(create_new=True)

    def end_group(self):
        self.inputs_pos = 0
        self.inputs[self.inputs_pos].set_input_selected()
        # self.thorpy_box = thorpy.Box(elements=list(map(lambda x: x.slider, self.inputs)))
        # box = self.thorpy_box
        # # we regroup all elements on a menu, even if we do not launch the menu
        # self.menu = thorpy.Menu(box)
        # # important : set the screen as surface for all elements
        # for element in self.menu.get_population():
        #     element.surface = self.ssurface.surface
        # # use the elements normally...
        # box.set_topleft((100, 100))
        # box.blit()
        # box.update()
        pass

    def notify_events(self, events):
        # self.menu.react(events)
        pass

    def get_surface(self):
        return self.ssurface

    def str_result(self):
        return SURVEY_Qs_DELIM.join([_i.str_result() for _i in self.inputs])

    def get_result(self) -> [(GameSurveyQs, str)]:
        res: [(GameSurveyQs, str)] = []
        [res.append(_i.get_user_inputs()) for _i in self.inputs]
        return res

