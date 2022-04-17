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
def fishfinderw():
    # TODO: Should come from backend
    with open("./tests/workflows.json") as f:
        return json.load(f)["KAUST Fish Counter"]

@pytest.fixture
def fishfinderm():
    # TODO: Should come from backend
    with open("./tests/models.json") as f:
        return json.load(f)["KAUST Fish Finder"]


@pytest.fixture
def fourtythreefishw():
    # TODO: Should come from backend
    with open("./tests/workflows.json") as f:
        return json.load(f)["KAUST Fourtythree Fish"]

@pytest.fixture
def fourtythreefishm():
    # TODO: Should come from backend
    with open("./tests/models.json") as f:
        return json.load(f)["FourtyThree Fish SSD"]

@pytest.fixture
def veheyew():
    # TODO: Should come from backend
    with open("./tests/workflows.json") as f:
        return json.load(f)["Vehicles Counter"]

@pytest.fixture
def veheyem():
    # TODO: Should come from backend
    with open("./tests/models.json") as f:
        return json.load(f)["Vehicles Counter"]

@pytest.fixture
def humanw():
    # TODO: Should come from backend
    with open("./tests/workflows.json") as f:
        return json.load(f)["Human Counter"]

@pytest.fixture
def humanm():
    # TODO: Should come from backend
    with open("./tests/models.json") as f:
        return json.load(f)["Human Counter"]


@pytest.fixture
def harbour():
    return {
        "type": "stream",
        "url": "https://www.youtube.com/watch?v=NwWgOilQuzw&t=4s",
        "resolution": "720p",
        "sample_every" :2,
        "provider": "youtube",
        "length": 60
    }

@pytest.fixture
def ezviz():
    return {
        "type": "stream",
        "ipv4": "139.64.63.135",
        "port": "554",
        "username": "admin",
        "password": "MWJUES",
        "sample_every" :10,
        "provider": "rtsp",
        "length": 60
    }


@pytest.fixture
def arabian_angelfish():
    return {
        "type": "file",
        "path": f"{DIR}/media/arabian_angelfish.mov",
        "sample_every" :1
    }

@pytest.fixture
def arabian_angelfish_short():
    return {
        "type": "file",
        "path": f"{DIR}/media/arabian_angelfish_short.mov",
        "sample_every" :1
    }

@pytest.fixture
def lutjanis():
    return {
        "type": "file",
        "path": "./tests/media/lutjanis.mov",
        "sample_every" :30
    }

@pytest.fixture
def vehicles():
    return {
        "type": "file",
        "path": "./tests/media/cam_04.mp4",
        "sample_every" :30
    }