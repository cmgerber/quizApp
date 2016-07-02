#!/usr/bin/env python
import pytest
import os


def runtests():
    os.environ["APP_CONFIG"] = "testing"
    pytest.main("tests -s")

if __name__ == "__main__":
    runtests()
