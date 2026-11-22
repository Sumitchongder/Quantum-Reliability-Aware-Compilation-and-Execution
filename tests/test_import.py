import importlib

import pytest

import qrace

MODULES = ["bench", "arms", "run", "features", "noise", "data", "models", "select", "eval"]


def test_package_imports():
    assert qrace.__version__ == "0.1.0"


@pytest.mark.parametrize("name", MODULES)
def test_module_imports(name):
    importlib.import_module(f"qrace.{name}")