"""Global pytest fixtures."""
import pytest
from app import create_app
from app.workflow import WorkflowFactory
import json 
import os

DIR = os.path.dirname(os.path.realpath(__file__))

WORKFLOWS_DIR = f"{DIR}/../../falcoeye_backend/initialization/workflows"

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
def ta_fishfinder():
    # TODO: Should come from backend
    with open(f"{WORKFLOWS_DIR}/kaust_fish_counter_threaded_async.json") as f:
        return json.load(f)["structure"]

@pytest.fixture
def ta_fishfinder_grpc():
    # TODO: Should come from backend
    with open(f"{WORKFLOWS_DIR}/kaust_fish_counter_threaded_async_grpc.json") as f:
        return json.load(f)["structure"]


@pytest.fixture
def cars_monitor_leaky():
    # TODO: Should come from backend
    with open(f"{WORKFLOWS_DIR}/car_monitor_leaky.json") as f:
        return json.load(f)

@pytest.fixture
def arabian_angelfish_monitor_leaky():
    # TODO: Should come from backend
    with open(f"{WORKFLOWS_DIR}/arabian_angelfish_leaky.json") as f:
        return json.load(f)

@pytest.fixture
def arabian_angelfish_monitor_leaky_grpc():
    # TODO: Should come from backend
    with open(f"{WORKFLOWS_DIR}/arabian_angelfish_leaky_grpc.json") as f:
        return json.load(f)