from common.gameconstants import ClientMsgReq
from common.gamesurvey import SurveyGridQHeaders, PreGQs, PreGGQs_1, PreGGQs_2, SURVEY_QSEQ_DELIM, \
    serialize_survey_grid_result, deserialize_survey_grid_result, serialize_survey_input_result, \
    deserialize_survey_input_result
from common.logger import log
from gui.gui_common.display import Display
from gui.survey.SurveyInput import SurveyInput
from gui.survey.surveyform import SurveyForm
from gui.survey.survey_grid import SurveyQuestionGrid


class PreGameSurvey:

    def __init__(self, send_survey_action, has_parent=True):
        self.survey = SurveyForm(self.on_submit, has_parent)
        self.add_input_fields()
        self.add_grid_1()
        self.add_grid_2()
        self.send_survey_result = send_survey_action

    def on_submit(self):
        i = self.survey.s_questions_seq[0]
        s0 = serialize_survey_input_result("PreGQs", i.get_result())
        g = self.survey.s_questions_seq[1]
        s1 = serialize_survey_grid_result("PreGGQs_1", g.gqh, g.get_result())
        g = self.survey.s_questions_seq[2]
        s2 = serialize_survey_grid_result("PreGGQs_2", g.gqh, g.get_result())
        ser_msg = SURVEY_QSEQ_DELIM.join([s0, s1, s2])
        log("SUBMIT PRE GAME SURVEY\n" + ser_msg)
        if self.send_survey_result is not None:
            log("about to send to server")
            self.send_survey_result(ClientMsgReq.PreGameSurvey, ser_msg)
        else:
            log("about to locally validate")
            ds0, ds1, ds2 = ser_msg.split(SURVEY_QSEQ_DELIM)
            si0 = deserialize_survey_input_result(ds0)
            sg1 = deserialize_survey_grid_result(ds1)
            sg2 = deserialize_survey_grid_result(ds2)
            print("PRE GAME DESERIALIZE values to track")
            print("\n".join([f"{q},{t}" for q, t in si0]))
            print("\n".join([f"{q},{r}" for q, r in sg1]))
            print("\n".join([f"{q},{r}" for q, r in sg2]))
        return True

    def add_input_fields(self):
        si = SurveyInput()
        self.survey.add_survey_question(si)

        pg = si.new_page(self.survey.surface)
        pg.add_input(PreGQs.Q1, 50)
        pg.add_input(PreGQs.Q2, 4)
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
        pg.add_input(PreGQs.Q8, 4)

        # ------------
        pg = si.new_page(self.survey.surface)

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

    s = PreGameSurvey(None, False)
    s.main()
