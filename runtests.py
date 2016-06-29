import pytest
import os

def runtests():
    os.environ["APP_CONFIG"] = "testing"
    pytest.main("tests")

if __name__ == "__main__":
    runtests()
