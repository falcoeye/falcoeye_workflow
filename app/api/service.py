import dateutil.parser
from flask import current_app

from app.utils import err_resp, internal_err_resp, message
from app.workflow.workflow import WorkflowFactory
import logging

class AnalysisService:
    # Used for testing purposes only
    ANALYSIS = {}
    @staticmethod
    def new_analysis(data):
        workflow_struct = data["workflow"]
        analysis = data["analysis"]
        
        # Creating workflow handler
        workflow = WorkflowFactory.create_from_dict(workflow_struct,analysis)
        async_run = analysis.get("async",True)
        if async_run:
            workflow.run_sequentially_async()
        else:
            workflow.run_sequentially()
        
        # Keep reference to check on status without going to backend
        if current_app.config.get("TESTING"):
            AnalysisService.ANALYSIS[analysis["id"]] = workflow

        resp = message(True, "Analysis started")
        return resp, 200

    @staticmethod
    def get_status(analysis_id):
        if analysis_id in AnalysisService.ANALYSIS:
            workflow = AnalysisService.ANALYSIS[analysis_id]
            response = workflow.status()
            return response,200
        else:
            return err_resp("Analysis not found!", "analysis_404", 404)
        
        