import os
import pandas as pd
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text, func, select, and_, or_, not_, desc, bindparam

from db_tables import metadata, Questions, Answers, Results, Students, StudentsTest, Graphs

# project_root = os.path.dirname(os.path.realpath('quizApp_Project/'))
# DATABASE = os.path.join(project_root, 'quizDB.db')
engine = create_engine('sqlite:///quizDB.db?check_same_thread=False', echo=True)
conn = engine.connect()
metadata.create_all(engine)

df_q = pd.read_excel('student_id_list_final.xlsx', 'questions consented')
df_h = pd.read_excel('student_id_list_final.xlsx', 'critiques consented')

for ix, data in df_q.iterrows():
    r = conn.execute(Students.update().\
                     where(Students.c.student_id == data.questions).\
                     values(opt_in=data.consented))

for ix, data in df_h.iterrows():
    r = conn.execute(Students.update().\
                     where(Students.c.student_id == data.Heuristics).\
                     values(opt_in=data.consented))
