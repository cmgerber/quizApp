import os
import pandas as pd

from quizApp.app import db
from quizApp.models import Questions, Answers, Results, Students, StudentsTest, Graphs

def main():

    df_q = pd.read_excel('student_id_list_final.xlsx', 'questions consented')
    df_h = pd.read_excel('student_id_list_final.xlsx', 'critiques consented')

    for _, data in df_q.iterrows():
        student = Student.query.get(data.questions)
        student.opt_in = data.consented
        db.session.add(student)
        """
        r = conn.execute(Students.update().\
                         where(Students.c.student_id == data.questions).\
                         values(opt_in=data.consented))
        """

    for _, data in df_h.iterrows():
        student = Student.query.get(data.Heuristics)
        student.opt_in = data.consented
        db.session.add(student)
        """
        r = conn.execute(Students.update().\
                         where(Students.c.student_id == data.Heuristics).\
                         values(opt_in=data.consented))
        """

    db.session.commit()

if __name__ == "__main__":
    main()
