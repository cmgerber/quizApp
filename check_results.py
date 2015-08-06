import os
import csv
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text, func, select, and_, or_, not_, desc, bindparam

from db_tables import metadata, Questions, Answers, Results, Students, StudentsTest, Graphs

project_root = os.path.dirname(os.path.realpath('quizApp_Project/'))
DATABASE = os.path.join(project_root, 'quizDB.db')
engine = create_engine('sqlite:///{0}?check_same_thread=False'.format(DATABASE), echo=True)
conn = engine.connect()
metadata.create_all(engine)

students = conn.execute(select([Students])).fetchall()

results = conn.execute(select([Results])).fetchall()

with open('student_table_list.csv', 'wb') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    [spamwriter.writerow(s) for s in students]

with open('results_table_list.csv', 'wb') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    [spamwriter.writerow(r) for r in results]

# st = conn.execute(select([StudentsTest])).fetchall()

# with open('studenttest_table_list.csv', 'wb') as csvfile:
#     spamwriter = csv.writer(csvfile, delimiter=',',
#                             quotechar='|', quoting=csv.QUOTE_MINIMAL)
#     [spamwriter.writerow(r) for r in st]
