from common.gameconstants import INIT_TILE_SIZE, TILE_ADJ_MULTIPLIER, NL_DELIM
from common.gamesurvey import GameSurveyQs, QHeader, PGGQs, SurveyGridQHeaders
from gui.button import RadioButton
from gui.gui_common.display import Display
from gui.gui_common.fontmixin import FontMixin
from gui.survey.surveyform import SurveyForm
from gui.survey.survey_question import SurveyQuestion


class SurveyQuestionGrid(FontMixin, SurveyQuestion):
    class Row(FontMixin, Display):
        def __init__(self, parent, font_size,
                     question: GameSurveyQs,
                     h_margin,
                     v_margin,
                     width,
                     lineoffset=1.5,
                     num_rb_options=0,
                     idnum=0):
            FontMixin.__init__(self)
            self.lineoffset = lineoffset
            self.set_font_size(font_size)
            self.question = question
            self.q_ft = self.render_texts(self.question.q)
            self.total_height_cells = -1
            self.set_total_height_cells()
            Display.__init__(self, h_margin, v_margin, width, self.total_height_cells)
            self.parent: SurveyQuestionGrid = parent
            self.idnum = idnum
            self.o: RadioButton = RadioButton(h_margin + 32, v_margin, 30, 2,
                                              text_offset=(0, 0),
                                              option_offset=(.5, 3.4),
                                              horizontal=True)
            [self.o.add_option(" ", show_caption=False, default_sel=2) for _ in range(num_rb_options)]

        def set_total_height_cells(self):
            font_ht = sum(map(lambda fs: fs.get_height(), self.q_ft))
            line_space_ht = 1 * self.lineoffset * INIT_TILE_SIZE
            self.total_height_cells = (font_ht + line_space_ht) // INIT_TILE_SIZE

        def draw(self, surface):
            for i, fs in enumerate(self.q_ft):
                font_pos = (self.x, self.y + (i * self.lineoffset * INIT_TILE_SIZE))
                surface.blit(fs, font_pos)
            self.o.draw(surface) if self.o is not None else None

        def get_user_inputs(self, h: QHeader) -> (PGGQs, QHeader):
            h.chosen = self.o.get_chosen_option_value()
            return self.question, h

    class QuestionGroup(FontMixin):
        def __init__(self, parent, start_x, start_y):
            super().__init__()
            self.parent: SurveyQuestionGrid = parent
            self.survey_questions: [SurveyQuestionGrid.Row] = []
            self.h_margin_cells, self.v_margin_cells = start_x, start_y
            self.questions: [GameSurveyQs] = []
            self.first_col_width, _ = Display.coord(18 * TILE_ADJ_MULTIPLIER, 0)

        def add_question(self, question: GameSurveyQs):
            self.questions.append(question)

        def draw(self, surface):
            [row.draw(surface) for row in self.survey_questions]

        def dountil(self, true_condition, action=None):
            for _r in self.survey_questions:
                if true_condition(_r):
                    action(_r) if action is not None else None
                    break

        def mouse_down(self, mouse):
            self.dountil(lambda _r: _r.o.click(*mouse))

        def mouse_up(self, mouse):
            self.dountil(lambda _r: _r.o.click(*mouse))

        def end_group(self):
            from functools import reduce
            lines = map(lambda x: (len(x.strip()), x),
                        reduce(lambda a, b: a + b,
                               map(lambda q: q.q.split(NL_DELIM), self.questions)))
            _, mx_text = max(lines, key=lambda x: x[0])
            # tot_lines = len(list(reduce(lambda a, b: a + b,
            #                             map(lambda q: q.split(NL_DELIM), self.questions)))) + len(self.questions)
            fsz = Display.get_target_fontsz(self.font_name, self.font_size, True, str(mx_text),
                                            self.first_col_width)
            self.set_font_size(fsz)
            # h = self.render_text(str(mx_text))[0].get_rect().height
            lineoffset = 1.5  # ((tot_lines * h) / INIT_TILE_SIZE)/tot_lines
            prev_row_ht = 0
            for i, question in enumerate(self.questions):
                v_offset = prev_row_ht if i != 0 else \
                    self.v_margin_cells
                sqr = SurveyQuestionGrid.Row(self, fsz, question,
                                             self.h_margin_cells,
                                             v_offset,
                                             self.first_col_width,
                                             lineoffset=lineoffset,
                                             num_rb_options=self.parent.cols,
                                             idnum=len(self.survey_questions))
                prev_row_ht = sqr.ymargin()
                self.survey_questions.append(sqr)

    def __init__(self, parent, h: SurveyGridQHeaders):
        FontMixin.__init__(self)
        SurveyQuestion.__init__(self)
        self.parent: SurveyForm = parent
        self.gqh: SurveyGridQHeaders = h
        # Display.__init__(self, 1, 1, 20, 20)
        header = h.h.header
        self.cols = len(header)
        mx_lines_per_col = max(map(lambda x: len(x.split(NL_DELIM)), header))
        self.header = [[] for _ in range(mx_lines_per_col)]
        for e in header:
            c_arr = e.split(NL_DELIM)
            for _i, _h in enumerate(self.header):
                t = c_arr[_i] if _i < len(c_arr) else " "
                _h.append(self.render_texts(t)[0])
        # self.header = [(_ci, _ct) for _ci, _ct in enumerate(column_template)]

        self.question_group: [SurveyQuestionGrid.QuestionGroup] = []
        self.q_grp_pos = 0
        self.grp_render_cells = (5, 8)

    def mouse_down(self, mouse):
        self.question_group[self.q_grp_pos].mouse_down(mouse)

    def mouse_up(self, mouse):
        self.question_group[self.q_grp_pos].mouse_up(mouse)

    def has_next(self):
        return self.q_grp_pos < len(self.question_group) - 1

    def move_next(self):
        self.q_grp_pos += 1

    def has_prev(self):
        return self.q_grp_pos > 0

    def move_prev(self):
        self.q_grp_pos -= 1

    def draw_header(self, surface):
        frst_col = self.question_group[0].first_col_width
        prev_x_len = [0 for _ in range(len(self.header[0]))]
        for y, row in enumerate(self.header):
            for x, col in enumerate(row):
                cum_x_offset = frst_col + sum([prev_x_len[a] for a in range(x)])
                st_x, st_y = Display.coord(self.grp_render_cells[0], self.grp_render_cells[1] - 6)
                font_pos = (cum_x_offset + (x * INIT_TILE_SIZE), st_y + (y * 1.5 * INIT_TILE_SIZE))
                prev_x_len[x] = col.get_width() if prev_x_len[x] < col.get_width() else prev_x_len[x]
                surface.blit(col, font_pos)

        # [he.draw(surface) for h_row in self.header for he in h_row]

    def draw(self, surface):
        self.draw_header(surface)
        self.question_group[self.q_grp_pos].draw(surface)

    def add_group(self):
        _grp = SurveyQuestionGrid.QuestionGroup(self, *self.grp_render_cells)
        self.question_group.append(_grp)
        return _grp

    def get_result(self) -> [(GameSurveyQs, QHeader)]:
        res: [(GameSurveyQs, QHeader)] = []
        for qg in self.question_group:
            [
                res.append(r.get_user_inputs(self.gqh.h.__copy__()))
                for r in qg.survey_questions
            ]
        return res

    def str_result(self):
        return "\n".join([f"{q},{r}" for q, r in self.get_result()])