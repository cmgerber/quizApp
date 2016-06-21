import os
import csv
from quizApp.models import Student, Result
from quizApp.app import db
from sqlalchemy import inspect

def write_row(writer, mapper, obj):
    row = []
    for column in mapper.c.keys():
        row.append(getattr(obj, column))

    writer.writerow(row)


def main():
    student_mapper = inspect(Student)
    result_mapper = inspect(Result)

    students = Student.query.all()
    results = Result.query.all()

    with open('student_table_list.csv', 'wb') as csvfile:

        student_writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for student in students:
            write_row(student_writer, student_mapper, student)

    with open('results_table_list.csv', 'wb') as csvfile:
        result_writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for result in results:
            write_row(result_writer, result_mapper, result)

if __name__ == "__main__":
    main()
