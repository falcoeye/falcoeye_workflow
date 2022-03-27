from flask import Blueprint, current_app
from flask_restx import Api
from .controller import analysis_ns

# Import controller APIs as namespaces.
api_bp = Blueprint("api", __name__)

api = Api(
    api_bp, title="API", description="Main routes."
)

# API namespaces
api.add_namespace(analysis_ns)