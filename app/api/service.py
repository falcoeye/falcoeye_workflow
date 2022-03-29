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
        # stream info
        stream      = data["stream"]
        stream_type = stream["type"]
        # workflow info
        workflow_structure = data["workflow"]["structure"]
        workflow_args      = data["workflow"]["args"]
        model              = data["workflow"]["model"]
        # analysis info
        analysis_id = data["analysis"]["id"]
        
        # Initializing model first
        modelHandler = ModelHandler.init(model)
        if not modelHandler:
            return internal_err_resp()

        # Creating workflow handler
        workflowWorker = WorkflowFactory.create(analysis_id,workflow_structure,workflow_args)

        # Creating AI sink to stream frames into
        sink = AISink(analysis_id,modelHandler,workflowWorker)

        if stream_type == "file":
            pass
        elif stream_type == "stream":
            url = stream["url"]
            provider = stream["provider"]
            resolution = stream["resolution"]
            sample_every = stream.get("sample_every",1)
            length = stream.get("length",60)
            streamWorker = WebStreamWorker(analysis_id,url,provider,resolution,sample_every,length,sink)
        
        # Registering analysis for status update
        AnalysisBank.register(analysis_id,workflowWorker)
        
        # Start model container if not running
        started = modelHandler.start()
        if not started:
            return internal_err_resp()
        
        # Start workflow 
        started = workflowWorker.start(AnalysisService.done_workflow)
        if not started:
            return internal_err_resp()

        # Start sink 
        started = sink.start()
        if not started:
            return internal_err_resp()
        
        # Start streamer
        started = streamWorker.start(AnalysisService.done_streaming)
        if not started:
            return internal_err_resp()    
            
        resp = message(True, "Anaysis has been started")
        return resp, 200
        

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