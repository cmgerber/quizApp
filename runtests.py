#!/usr/bin/env python
import pytest
import os


def runtests():
    os.environ["APP_CONFIG"] = "testing"
    return pytest.main("tests")

if __name__ == "__main__":
    exit(runtests())
