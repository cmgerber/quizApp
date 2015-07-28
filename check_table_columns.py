from sqlalchemy import create_engine
engine = create_engine('sqlite:///quizDB.db?check_same_thread=False', echo=True)

from sqlalchemy import inspect
inspector = inspect(engine)

for table_name in inspector.get_table_names():
   for column in inspector.get_columns(table_name):
       print("Column: %s" % column['name'])
