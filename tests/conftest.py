"""Global pytest fixtures."""
import pytest

from app import create_app
from app.workflow import AnalysisBank,WorkflowFactory

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
def bank():
    AnalysisBank.init()

@pytest.fixture
def factory():
    WorkflowFactory.init("./workflows.json")