#!/usr/bin/env python
"""Management script for common operations.
"""

import click
import pytest
from flask.cli import FlaskGroup
from quizApp import create_app


@click.pass_context
def get_app(ctx, _):
    """Create an app with the correct config.
    """
    return create_app(ctx.parent.params["config"])


@click.option("-c", "--config", default="development")
@click.group(cls=FlaskGroup, create_app=get_app)
def cli(**_):
    """Define the top level group.
    """
    pass


@cli.command("test")
def test():
    """Set the app config to testing and run pytest, passing along command
    line args.
    """
    return pytest.main(["--cov=quizApp",
                        "--flake8",
                        "--pylint",
                        "./"])

if __name__ == '__main__':
    cli()
