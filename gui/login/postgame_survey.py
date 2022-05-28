from common.gameconstants import ClientMsgReq
from common.gamesurvey import SurveyGridQHeaders, PreGQs, PreGGQs_1, PreGGQs_2, PGGQs, PGIQs, \
    serialize_survey_grid_result, serialize_survey_input_result, SURVEY_QSEQ_DELIM, deserialize_survey_grid_result, \
    deserialize_survey_input_result
from common.logger import log
from gui.gui_common.display import Display
from gui.survey.surveyform import SurveyForm
from gui.survey.survey_grid import SurveyQuestionGrid
from gui.survey.survey_multiinetext import SurveyQuestionInputText


class PostGameSurvey:

    def __init__(self, send_survey_action, has_parent=True):
        self.survey = SurveyForm(self.on_submit, has_parent)
        self.add_post_game_survey_grid()
        self.add_post_game_survey_inputs()
        self.send_survey_result = send_survey_action

    def main(self):
        self.survey.main()

    def on_submit(self):
        g = self.survey.s_questions_seq[0]
        s1 = serialize_survey_grid_result("PGGQs", g.gqh, g.get_result())
        s2 = serialize_survey_input_result("PGIQs", self.survey.s_questions_seq[1].get_result())
        ser_msg = SURVEY_QSEQ_DELIM.join([s1, s2])
        log("SUBMIT POST GAME SURVEY\n" + ser_msg)
        if self.send_survey_result is not None:
            self.send_survey_result(ClientMsgReq.PostGameSurvey, ser_msg)
        else:
            ds1, ds2 = ser_msg.split(SURVEY_QSEQ_DELIM)
            sg = deserialize_survey_grid_result(ds1)
            si = deserialize_survey_input_result(ds2)
            print("POST GAME DESERIALIZE values to track")
            print("\n".join([f"{q},{r}" for q, r in sg]))
            print("\n".join([f"{q},{t}" for q, t in si]))
        return True

    def add_post_game_survey_grid(self):
        q1 = "1.	Please rate the below sentences:"
        sqg = SurveyQuestionGrid(self, SurveyGridQHeaders.H1)

        questions = [
            [PGGQs.Q1, PGGQs.Q2, PGGQs.Q3, PGGQs.Q4, PGGQs.Q5, PGGQs.Q6],
            [PGGQs.Q7, PGGQs.Q8, PGGQs.Q9, PGGQs.Q10, PGGQs.Q11, PGGQs.Q12],
            [PGGQs.Q13, PGGQs.Q14, PGGQs.Q15, PGGQs.Q16],
            [PGGQs.Q17, PGGQs.Q18, PGGQs.Q19],
        ]

        for _q_grp in questions:
            _sqg_grp = sqg.add_group()
            for _q in _q_grp:
                _sqg_grp.add_question(_q)
            _sqg_grp.end_group()

        self.survey.add_survey_question(sqg)

    def add_post_game_survey_inputs(self):
        sit = SurveyQuestionInputText(self.survey.surface)
        sit.add_survey_question(PGIQs.Q1, 450)
        sit.add_survey_question(PGIQs.Q2, 450)
        sit.end_group()
        sit.disable()

        self.survey.add_survey_question(sit)


if __name__ == '__main__':
    Display.init()

    s = PostGameSurvey(None, False)
    s.main()
