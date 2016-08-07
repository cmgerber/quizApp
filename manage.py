import os
import sys
import click
import pytest
from sqlalchemy.engine.url import make_url
from flask import current_app
from flask.cli import FlaskGroup
from sqlalchemy.exc import OperationalError
import pdb
from quizApp import create_app


@click.pass_context
def get_app(ctx, info):
    return create_app(ctx.parent.params["config"])


@click.option("-c", "--config", default="development")
@click.group(cls=FlaskGroup, create_app=get_app)
def cli(config):
    pass


@cli.command("test")
@click.pass_context
def test(ctx):
    """Set the app config to testing and run pytest, passing along command
    line args.
    """
    return pytest.main(["--cov=quizApp",
                        "--flake8",
                        "--pylint",
                        "./"])


if __name__ == '__main__':
    cli()
