from flask import request
from flask_restx import Resource
from flask_restx import Namespace

from app.utils import validation_error
from .dto import AnalysisDto
from .service import AnalysisService

api_analysis = Namespace("analysis", description="Analysis related operations.")




@api_analysis.route("/")
class Analysis(Resource):
    def post(self):
        analysis_data = request.get_json()
        return AnalysisService.new_analysis(analysis_data)


@api_analysis.route("/predicted/<analysis_id>")
class AnalysisAIStatus(Resource):
    def post(self):
        prediction_data = request.get_json()
        return AnalysisService.predicted(analysis_id,prediction_data)