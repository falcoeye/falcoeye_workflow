from flask import request
from flask_restx import Resource
from flask_restx import Namespace
from flask import Blueprint, current_app
from flask_restx import Api
from app.utils import validation_error
from .service import AnalysisService



analysis_bp = Blueprint("analysis", __name__)

analysis_ns = Namespace("analysis", description="Analysis related operations.")



@analysis_ns.route("/")
class Analysis(Resource):
    def post(self):
        analysis_data = request.get_json()
        return AnalysisService.new_analysis(analysis_data)



@analysis_ns.route("/status/<analysis_id>")
class AnalysisStatus(Resource):
    def get(self,analysis_id):
        return AnalysisService.get_status(analysis_id)