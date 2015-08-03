activate_this = '/projects/oev/quizApp_Project/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys
base_path = "/projects/oev/quizApp_Project"
if base_path not in sys.path:
    sys.path.insert(0,base_path)

from quizApp import app as application
