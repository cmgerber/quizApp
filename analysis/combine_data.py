import os
import csv

from quizApp.models import Questions, Answers, Results, Students, StudentsTest, Graphs

def main():
    #students = conn.execute(select([Students])).fetchall()
    students = Student.query.all()

    results = Result.query.\
            join(Student).\
            outerjoin(StudentTest).\
            outerjoin(Question).\
            outerjoin(Answer).\
            add_columns(Answer.answer,
                        Question.id,
                        Question.question,
                        Question.question_type,
                        StudentTest.dataset,
                        StudentTest.test).\
            filter(Student.opt_in == "yes").all()

    #TODO: this still requires some finishing
    """
    results = conn.execute(select([Results.c.student_id,
                                    Results.c.student_test_id,
                                    Results.c.results_id,
                                    Results.c.answer,
                                    Results.c.graph_id,
                                   Answers.c.answer,
                                   Questions.c.question_id,
                                   Questions.c.question,
                                   Questions.c.question_type,
                                   StudentsTest.c.dataset,
                                   StudentsTest.c.test]).\
                           select_from(Results.join(Students,
                                        Students.c.student_id == Results.c.student_id).\
                           outerjoin(StudentsTest,
                                     StudentsTest.c.student_test_id == Results.c.student_test_id).\
                           outerjoin(Questions,
                                     Questions.c.question_id == StudentsTest.c.question_id).\
                           outerjoin(Answers,
                                     Answers.c.answer_id == Results.c.answer)).\
                           where(Students.c.opt_in == 'yes')).fetchall()
    """

    results = [[x.replace(',', '') if type(x) == type('s') else x for x in t] for t in results]
    results = [[' '.join(x.splitlines()) if type(x) == type('s') else x for x in t] for t in results]
    results = [['Student_id', 'Student_Test_id', 'Result_id',
                'answer', 'graph_id', 'answer_text', 'question_id',
                'question', 'Question_type', 'dataset', 'test']] + results

    with open('student_table_list.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        [spamwriter.writerow(s) for s in students]

    with open('results_table_list.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        [spamwriter.writerow(r) for r in results]

if __name__ == "__main__":
    main()
