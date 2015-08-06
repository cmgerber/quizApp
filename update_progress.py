import os
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


ids = [x[0] for x in conn.execute(select([Students.c.student_id])).fetchall()]

print (ids)

for sid in ids:
    r = conn.execute(Students.update().\
                     where(Students.c.student_id == sid).\
                     values(progress='post_test'))
