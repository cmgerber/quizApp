Platform for asking questions based on visualizations.

## Installation

    pip install -r requirements.txt
    mysql -u root -p < setup_db.sql
    python populate_students_db.py

## Running

    python runserver.py

## Using

After running the code, it should tell you where it is running. You can
then navigate to this address in a browser to use the quiz platform.

## Branches

- `master`: This branch contains stable releases of the code.

- `develop`: Feature development and as-yet untested code lives in
    this branch before it is merged into `master`.
