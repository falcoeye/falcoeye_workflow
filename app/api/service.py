import dateutil.parser
from flask import current_app

from app import db
from app.utils import err_resp, internal_err_resp, message
from app.streamer import WebStreamWorker
from app.io.sink import AISink
from app.workflow.workflow import WorkflowFactory
from app.ai import ModelHandler
from app.workflow import AnalysisBank


class AnalysisService:
    @staticmethod
    def new_analysis(data):
        stream = data["stream"]
        workflow = data["workflow"]
        stream_type = stream["type"]
        analysis_id = data["analysis"]["id"]
        model = workflow["model"]
        
        modelHandler = ModelHandler.init(model)
        

        if not modelHandler:
            return internal_err_resp()

        if stream_type == "file":
            pass
        elif stream_type == "stream":
            url = stream["url"]
            provider = stream["provider"]
            resolution = stream["resolution"]
            sample_every = stream.get("sample_every",1)
            length = stream.get("length",60)
            workflowWorker = WorkflowFactory.create(analysis_id,workflow)
            sink = AISink(analysis_id,modelHandler,workflowWorker)
            streamWorker = WebStreamWorker(analysis_id,url,provider,resolution,sample_every,length,sink)
        

        AnalysisBank.register(analysis_id,workflowWorker)
        
        running = modelHandler.run()
        if not running:
            return internal_err_resp()
        try:
            streamWorker.start(AnalysisService.done_streaming)
            print("streaming started")
            workflowWorker.start(AnalysisService.done_workflow)
            resp = message(True, "Analysis started")
            return resp, 200

        except Exception as error:
            raise
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def predicted(aid,prediction_data):
        AnalysisBank.put(aid,prediction_data)

    @staticmethod
    def done_streaming(aid):
        AnalysisBank.done_streaming(aid)
    
    @staticmethod
    def done_workflow(aid):
        AnalysisBank.done_workflow(aid)
    
    @staticmethod
    def get_status(analysis_id):
        return AnalysisBank.get_status(analysis_id)