#!/usr/bin/env python
import pytest
import os
import sys


def runtests():
    os.environ["APP_CONFIG"] = "testing"
    return pytest.main(["--cov-report", "xml:.coverage",
                        "--cov=quizApp",
                        "tests/"] + sys.argv)

if __name__ == "__main__":
    exit(runtests())
