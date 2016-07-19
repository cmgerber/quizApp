"""Various functions that are useful in multiple views.
"""
from flask import abort


def validate_model_id(model, model_id, code=404):
    """Given a model and id, retrieve and return that model from the database
    or abort with the given code.
    """
    obj = model.query.get(model_id)

    if not obj:
        abort(code)

    return obj
