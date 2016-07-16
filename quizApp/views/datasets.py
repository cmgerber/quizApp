"""Views for CRUD datasets.
"""

from flask import Blueprint, render_template, url_for, jsonify, abort
from flask_security import roles_required

from quizApp.models import Dataset, Graph
from quizApp.forms.common import DeleteObjectForm
from quizApp.forms.datasets import DatasetForm
from quizApp import db
from quizApp.views.helpers import validate_model_id


datasets = Blueprint("datasets", __name__, url_prefix="/datasets")


@datasets.route('/', methods=["GET"])
@roles_required("experimenter")
def read_datasets():
    """Display a list of all datasets.
    """
    datasets_list = Dataset.query.all()
    create_dataset_form = DatasetForm()

    return render_template("datasets/read_datasets.html",
                           datasets=datasets_list,
                           create_dataset_form=create_dataset_form)


@datasets.route('/', methods=["POST"])
@roles_required("experimenter")
def create_dataset():
    """Create a new dataset.
    """
    create_dataset_form = DatasetForm()

    if not create_dataset_form.validate():
        return jsonify({"success": 0, "errors": create_dataset_form.errors})

    dataset = Dataset()
    create_dataset_form.populate_dataset(dataset)

    dataset.save()

    return jsonify({"success": 1})


@datasets.route('/<int:dataset_id>/', methods=["POST"])
@roles_required("experimenter")
def update_dataset(dataset_id):
    """Change the properties of this dataset.
    """
    dataset = validate_model_id(Dataset, dataset_id)

    update_dataset_form = DatasetForm()

    if not update_dataset_form.validate():
        return jsonify({"success": 0, "errors": update_dataset_form.errors})

    update_dataset_form.populate_dataset(dataset)

    db.session.commit()

    return jsonify({"success": 1})


@datasets.route('/<int:dataset_id>/', methods=["DELETE"])
@roles_required("experimenter")
def delete_dataset(dataset_id):
    """Delete this dataset.
    """
    dataset = validate_model_id(Dataset, dataset_id)

    db.session.delete(dataset)
    db.session.commit()

    return jsonify({"success": 1,
                    "next_url": url_for('datasets.read_datasets')})


@datasets.route('/<int:dataset_id>/graphs/<int:graph_id>', methods=["DELETE"])
@roles_required("experimenter")
def delete_dataset_graph(dataset_id, graph_id):
    """Delete a particular graph in a particular dataset.
    """
    dataset = validate_model_id(Dataset, dataset_id)
    graph = validate_model_id(Graph, graph_id)

    if graph not in dataset.graphs:
        abort(404)

    db.session.delete(graph)
    db.session.commit()

    return jsonify({"success": 1})


@datasets.route('/<int:dataset_id>/graphs/<int:graph_id>', methods=["GET"])
@roles_required("experimenter")
def read_graph(dataset_id, graph_id):
    """Get an html representation of a particular graph.
    """
    dataset = validate_model_id(Dataset, dataset_id)
    graph = validate_model_id(Graph, graph_id)

    if graph not in dataset.graphs:
        abort(404)

    return render_template("datasets/read_graph.html", graph=graph)


@datasets.route('/<int:dataset_id>/settings', methods=["GET"])
@roles_required("experimenter")
def settings_dataset(dataset_id):
    """View the configuration of a particular dataset.
    """
    dataset = validate_model_id(Dataset, dataset_id)

    update_dataset_form = DatasetForm()

    update_dataset_form.populate_fields(dataset)

    delete_dataset_form = DeleteObjectForm()

    return render_template("datasets/settings_dataset.html",
                           dataset=dataset,
                           update_dataset_form=update_dataset_form,
                           delete_dataset_form=delete_dataset_form)
