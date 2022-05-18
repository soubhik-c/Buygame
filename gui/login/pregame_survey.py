from common.gamesurvey import SurveyGridQHeaders, PreGQs, PreGGQs_1, PreGGQs_2
from gui.gui_common.display import Display
from gui.survey.SurveyInput import SurveyInput
from gui.survey.surveyform import SurveyForm
from gui.survey.survey_grid import SurveyQuestionGrid


class PreGameSurvey:

    def __init__(self):
        self.survey = SurveyForm(None, False)

    def add_input_fields(self):
        si = SurveyInput()
        self.survey.add_survey_question(si)

        pg = si.new_page()
        pg.add_input(PreGQs.Q1, 50)
        pg.add_input(PreGQs.Q2, 5)
        pg.add_options(PreGQs.Q3,
                       [
                           "American Indian or Alaskan native",
                           "Asian/Pacific Islander",
                           "Black or African American",
                           "Hispanic American",
                           "White/Caucasian",
                           "Prefer not to respond"
                       ])
        pg.add_options(PreGQs.Q4,
                       [
                           "English",
                           "Other (please specify):"
                       ])

        pg.add_options(PreGQs.Q5,
                       [
                           "Male",
                           "Female",
                           "Non-binary/Third gender",
                           "Prefer not to respond"
                       ])

        pg.switch_to_right_column()
        pg.add_line_break(4)

        pg.add_options(PreGQs.Q6,
                       [
                           "College",
                           "Masters",
                           "Doctorate",
                           "Other"
                       ])

        pg.add_options(PreGQs.Q7,
                       [
                           "Employed full-time (40 + hours a week)",
                           "Employed part-time (less than 40 hours a week)",
                           "Unemployed (currently looking for a job)",
                           "Unemployed (currently not looking for a job)",
                           "Self-employed/Working in the family business"
                       ])

        pg.add_line_break()
        pg.add_input(PreGQs.Q8, 5)

        # ------------
        pg = si.new_page()

        pg.add_options(PreGQs.Q9,
                       [
                           "Every day",
                           "Once a week",
                           "Less than 4 times a month",
                           "Never "
                       ])
        pg.add_options(PreGQs.Q10,
                       [
                           "I don’t read unless forced to",
                           "Less than 15 minutes",
                           "15 - 30 minutes",
                           "30 minutes to 1 hour",
                           "More than an hour"
                       ])
        pg.add_options(PreGQs.Q11,
                       [
                           "School / University Assignments",
                           "Recommendation from friends",
                           "Need for Information",
                           "I enjoy reading",
                           "Relaxation activity"
                       ])

    def add_grid_1(self):
        caption = PreGQs.Q12
        sqg = SurveyQuestionGrid(self, SurveyGridQHeaders.H2)

        questions = [
            [PreGGQs_1.Q1, PreGGQs_1.Q2, PreGGQs_1.Q3, PreGGQs_1.Q4, PreGGQs_1.Q5,
             PreGGQs_1.Q6, PreGGQs_1.Q7],
        ]
        self.add_grid_Qs(sqg, questions)

    def add_grid_2(self):
        caption = PreGQs.Q13
        sqg = SurveyQuestionGrid(self, SurveyGridQHeaders.H1)

        questions = [
            [PreGGQs_2.Q1, PreGGQs_2.Q2, PreGGQs_2.Q3, PreGGQs_2.Q4, PreGGQs_2.Q5, PreGGQs_2.Q6],
            [PreGGQs_2.Q7, PreGGQs_2.Q8, PreGGQs_2.Q9, PreGGQs_2.Q10],
        ]
        self.add_grid_Qs(sqg, questions)

    def add_grid_Qs(self, sqg, questions):
        for _q_grp in questions:
            _sqg_grp = sqg.add_group()
            for _q in _q_grp:
                _sqg_grp.add_question(_q)
            _sqg_grp.end_group()

        self.survey.add_survey_question(sqg)

    def main(self):
        self.survey.main()


if __name__ == '__main__':
    Display.init()

    s = PreGameSurvey()
    s.add_input_fields()
    s.add_grid_1()
    s.add_grid_2()
    s.main()
