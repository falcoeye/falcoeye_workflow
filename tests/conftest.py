"""Global pytest fixtures."""
import pytest
from app import create_app
from app.workflow import WorkflowFactory
import json 
import os

DIR = os.path.dirname(os.path.realpath(__file__))

@pytest.fixture
def app():
    app = create_app("testing")
    app.testing = True
    return app

@pytest.fixture
def client(app):
    with app.app_context():
        with app.test_client() as client:
            yield client

@pytest.fixture
def fishfinder():
    # TODO: Should come from backend
    with open("./workflows/kaust_fish_counter.json") as f:
        return json.load(f)

@pytest.fixture
def ta_fishfinder():
    # TODO: Should come from backend
    with open("./workflows/kaust_fish_counter_threaded_async.json") as f:
        return json.load(f)


@pytest.fixture
def arabian_angelfish():
    # TODO: Should come from backend
    with open("./workflows/arabian_angelfish.json") as f:
        return json.load(f)

@pytest.fixture
def arabian_angelfish_sequential():
    # TODO: Should come from backend
    with open("./workflows/arabian_angelfish_sequential.json") as f:
        return json.load(f)
