import pygame_widgets
import pygame
from pygame.constants import KEYUP, K_ESCAPE, VIDEORESIZE

from common.gameconstants import TILE_ADJ_MULTIPLIER, FPS, Colors
from common.gamesurvey import PGGQs, SurveyGridQHeaders, PGIQs, SURVEY_QSEQ_DELIM, \
    serialize_survey_grid_result, deserialize_survey_input_result, \
    serialize_survey_input_result, deserialize_survey_grid_result
from common.logger import logger, log
from gui.button import TextButton
from gui.gui_common.display import Display
from gui.gui_common.subsurface import SubSurface
from gui.survey.survey_grid import SurveyQuestionGrid
from gui.survey.survey_multiinetext import SurveyQuestionInputText
from gui.survey.survey_question import SurveyQuestion


class SurveyForm(SubSurface):
    def __init__(self, submit_action: (), has_parent=True):
        super(SurveyForm, self).__init__()
        self._layer = SubSurface._SS_BASE_LAYER
        self.s_questions_seq: [SurveyQuestion] = []
        self.s_questions_pos = 0
        h_mrg, v_mrg = self.xmargin() - 12, self.ymargin() - 5
        self.prev_button = TextButton(h_mrg - (4 * TILE_ADJ_MULTIPLIER),
                                      v_mrg,
                                      7, 3, Colors.GREEN,
                                      "prev",
                                      visual_effects=True)
        self.next_button = TextButton(h_mrg,
                                      v_mrg,
                                      7, 3, Colors.GREEN,
                                      "next",
                                      visual_effects=True)

        self.prev_button.hide()
        self.submit = False
        self.submit_act = submit_action
        self.run = True
        self.has_parent = has_parent

    def main(self, input_game=None):
        clock = pygame.time.Clock()
        from gui.gameui import GameUI
        assert input_game is None or isinstance(input_game, GameUI)
        g: GameUI = input_game
        logger.reset()
        while self.run:
            clock.tick(FPS)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse = self.mousexy()
                    self.mouse_down(mouse)

                elif event.type == pygame.MOUSEBUTTONUP:
                    mouse = self.mousexy()
                    self.mouse_up(mouse)
                    pygame.event.clear([pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.KEYUP])

                    #
                    # if self.login_button is not None and \
                    #         self.login_button.click(ss_mx, ss_my):
                    #     self.login_button.mouse_up()
                    #     self.login()
                    #     continue
                    #
                    # if self.user_choices is not None:
                    #     self.user_choices.click(ss_mx, ss_my)
                    #     continue

                elif event.type == pygame.QUIT or \
                        (event.type == KEYUP and event.key == K_ESCAPE):
                    if not self.has_parent:
                        self.run = False
                        pygame.quit()
                        quit()

                elif event.type == VIDEORESIZE:
                    # screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    Display.resize(event, g.refresh_resolution) if g is not None else None
                elif event.type == pygame.KEYUP:
                    self.s_questions_seq[self.s_questions_pos].key_up(event)
                    # if event.key == pygame.K_RETURN:
                    #     self.move_next_control(event)
                    # else:
                    #     pass

            self.draw(events)

    def draw(self, events):
        if not self.has_parent:
            Display.surface().fill(Colors.BLACK.value)
        super().draw(events)
        self.prev_button.draw(self.surface)
        self.next_button.draw(self.surface)
        self.s_questions_seq[self.s_questions_pos].draw(self.surface)
        pygame_widgets.update(events)
        pygame.display.update()

    def mouse_down(self, mouse):
        if self.next_button.click(*mouse):
            self.next_button.mouse_down()
            return
        elif self.prev_button.click(*mouse):
            self.prev_button.mouse_down()
            return

        ce = self.s_questions_seq[self.s_questions_pos]
        ce.mouse_down(mouse)

    def mouse_up(self, mouse):
        ce = self.s_questions_seq[self.s_questions_pos]
        if self.next_button.click(*mouse):
            try:
                if self.submit:
                    self.submit_survey()
                    return

                if ce.has_next():
                    ce.move_next()
                    return

                if self.has_next():
                    ce.disable()
                    self.s_questions_pos += 1
                    ce = self.s_questions_seq[self.s_questions_pos]
                    ce.enable()
            finally:
                if not self.has_next():
                    self.next_button.set_text("submit")
                    self.submit = True

                self.prev_button.show()
                self.next_button.mouse_up()
        elif self.prev_button.click(*mouse):
            try:
                if ce.has_prev():
                    ce.move_prev()
                    return

                if self.has_prev():
                    ce.disable()
                    self.s_questions_pos -= 1
                    ce = self.s_questions_seq[self.s_questions_pos]
                    ce.enable()
            finally:
                if not self.has_prev():
                    self.prev_button.hide()

                self.submit = False
                self.next_button.set_text("next")
                self.prev_button.mouse_up()
        elif ce.mouse_up(mouse):
            pass

    def has_prev(self):
        return self.s_questions_pos > 0 or self.s_questions_seq[self.s_questions_pos].has_prev()

    def has_next(self):
        return self.s_questions_pos < len(self.s_questions_seq) - 1

    def add_survey_question(self, ques: SurveyQuestion):
        self.s_questions_seq.append(ques)

    def submit_survey(self):
        g = self.s_questions_seq[0]
        s1 = serialize_survey_grid_result(g.gqh, g.get_result())
        s2 = serialize_survey_input_result(self.s_questions_seq[1].get_result())
        msg = SURVEY_QSEQ_DELIM.join([s1, s2])
        log("SUBMIT SURVERY\n" + msg)
        if self.submit_act is not None:
            self.submit_act(msg)
        else:
            ds1, ds2 = msg.split(SURVEY_QSEQ_DELIM)
            sg = deserialize_survey_grid_result(ds1)
            si = deserialize_survey_input_result(ds2)
            print("SB: DESER values to track")
            print("\n".join([f"{q},{r}" for q, r in sg]))
            print("\n".join([f"{q},{t}" for q, t in si]))
        self.run = False

