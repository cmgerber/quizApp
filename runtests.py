#!/usr/bin/env python
import pytest
import os
import sys


def runtests():
    os.environ["APP_CONFIG"] = "testing"
    return pytest.main(["tests"] + sys.argv)

if __name__ == "__main__":
    exit(runtests())
