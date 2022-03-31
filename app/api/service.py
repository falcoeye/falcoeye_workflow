import dateutil.parser
from flask import current_app

from app.utils import err_resp, internal_err_resp, message
from app.streamer import WebStreamWorker,FileStreamWorker
from app.io.sink import AISink
from app.workflow.workflow import WorkflowFactory
from app.ai import ModelHandler


class AnalysisService:
    # Used for testing purposes only
    ANALYSIS = {}
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

        print("Workflow created")

        # Keep reference to check on status without going to backend
        if current_app.config.get("TESTING"):
            AnalysisService.ANALYSIS[analysis_id] = workflowWorker

        # Creating AI sink to stream frames into
        sink = AISink(analysis_id,modelHandler,workflowWorker)

        print("Sink created")

        if stream_type == "file":
            sample_every = stream.get("sample_every",1)
            filepath = stream["path"]
            streamWorker = FileStreamWorker(workflowWorker,filepath,sample_every,sink)

        elif stream_type == "stream":
            url = stream["url"]
            provider = stream["provider"]
            resolution = stream["resolution"]
            sample_every = stream.get("sample_every",1)
            length = stream.get("length",60)
            streamWorker = WebStreamWorker(workflowWorker,url,provider,resolution,sample_every,length,sink)

        print("Stream created")

        # Start model container if not running
        started = modelHandler.start()
        if not started:
            return internal_err_resp()
        
        print("Model worker started")

        # Start workflow 
        started = workflowWorker.start()
        if not started:
            return internal_err_resp()

        print("Workflow worker started")

        # Start sink 
        started = sink.start()
        if not started:
            return internal_err_resp()
        
        print("Sink worker started")

        # Start streamer
        started = streamWorker.start()
        if not started:
            return internal_err_resp()

        print("Streamer worker started")    

        resp = message(True, "Anaysis has been started")
        return resp, 200

    @staticmethod
    def get_status(analysis_id):
        if analysis_id in AnalysisService.ANALYSIS:
            worker = AnalysisService.ANALYSIS[analysis_id]
            response = {
                "workflow_status": worker.is_running(),
                "sinking_status": worker.is_sinking(),
                "streaming_status": worker.is_streaming()
            }  
            return response,200
        else:
            return err_resp("Analysis not found!", "analysis_404", 404)
        
        