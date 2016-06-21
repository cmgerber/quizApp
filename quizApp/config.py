import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = '}D\x04\x184\x14\xa7\xd7\xda\x93\xaa|\xa6\xed\xc4\x85\xf2W\xa3\x93\xda\x08\x80X'
    SQLALCHEMY_DATABASE_URI = "sqlite:///../quizDB.db"
