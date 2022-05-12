from common.gamesurvey import SurveyGridQHeaders, PreGQs, PreGGQs_1, PreGGQs_2, PGGQs, PGIQs
from gui.gui_common.display import Display
from gui.survey.surveyform import SurveyForm
from gui.survey.survey_grid import SurveyQuestionGrid
from gui.survey.survey_multiinetext import SurveyQuestionInputText


class PostGameSurvey:

    def __init__(self):
        self.survey = SurveyForm(None, False)

    def main(self):
        self.survey.main()

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
        sit = SurveyQuestionInputText(self)
        sit.add_survey_question(PGIQs.Q1, 450)
        sit.add_survey_question(PGIQs.Q2, 450)
        sit.end_group()
        sit.disable()

        self.survey.add_survey_question(sit)


if __name__ == '__main__':
    Display.init()

    s = PostGameSurvey()
    s.add_post_game_survey_grid()
    s.add_post_game_survey_inputs()
    s.main()
