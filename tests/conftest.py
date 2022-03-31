"""Global pytest fixtures."""
import pytest
from app import create_app
from app.workflow import WorkflowFactory
import json 

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
def arabian_angelfish():
    return {
        "type": "file",
        "path": "./tests/arabian_angelfish_short.mov",
        "sample_every" :1
    }

@pytest.fixture
def lutjanis():
    return {
        "type": "file",
        "path": "./tests/lutjanis.mov",
        "sample_every" :30
    }