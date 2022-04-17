import dateutil.parser
from flask import current_app

from app.utils import err_resp, internal_err_resp, message
from app.streamer import WebStreamWorker,FileStreamWorker
from app.io.sink import AISink
from app.workflow.workflow import WorkflowFactory,LocalStreamingWorkFlowHandler,RemoteStreamingWorkflowHandler
from app.ai import ModelHandler
import logging

class AnalysisService:
    # Used for testing purposes only
    ANALYSIS = {}
    @staticmethod
    def new_analysis(data):
        remotestream = data.get("remote_stream",False)
        if not remotestream:
            AnalysisService.new_local_stream_analysis(data)
        else:
            AnalysisService.new_remote_stream_analysis(data)

    @staticmethod
    def new_remote_stream_analysis(data):
        
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
        workflowWorker = WorkflowFactory.create(analysis_id,workflow_structure,workflow_args,"remote",**stream)

        logging.info("Workflow created")

        # Keep reference to check on status without going to backend
        if current_app.config.get("TESTING"):
            AnalysisService.ANALYSIS[analysis_id] = workflowWorker


        # Start model container if not running
        started = modelHandler.start()
        if not started:
            return internal_err_resp()
        
        logging.info("Model worker started")

        # Start workflow 
        started = workflowWorker.start()
        if not started:
            return internal_err_resp()

        logging.info("Workflow worker started")

        resp = message(True, "Anaysis has been started")
        return resp, 200
    
    @staticmethod
    def new_local_stream_analysis(data):
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
        workflowWorker = WorkflowFactory.create(analysis_id,workflow_structure,workflow_args,"local")

        logging.info("Workflow created")

        # Keep reference to check on status without going to backend
        if current_app.config.get("TESTING"):
            AnalysisService.ANALYSIS[analysis_id] = workflowWorker

        # Creating AI sink to stream frames into
        sink = AISink(analysis_id,modelHandler,workflowWorker)

        logging.info("Sink created")

        if stream_type == "file":
            sample_every = stream.get("sample_every",1)
            filepath = stream["path"]
            streamWorker = FileStreamWorker(workflowWorker,filepath,sink,sample_every)

        elif stream_type == "stream":
            streamWorker = WebStreamWorker(workflowWorker,sink,**stream)

        logging.info("Stream created")

        # Start model container if not running
        started = modelHandler.start()
        if not started:
            return internal_err_resp()
        
        logging.info("Model worker started")

        # Start workflow 
        started = workflowWorker.start()
        if not started:
            return internal_err_resp()

        logging.info("Workflow worker started")

        # Start sink 
        started = sink.start()
        if not started:
            return internal_err_resp()
        
        logging.info("Sink worker started")

        # Start streamer
        started = streamWorker.start()
        if not started:
            return internal_err_resp()

        logging.info("Streamer worker started")    

        resp = message(True, "Anaysis has been started")
        return resp, 200

    @staticmethod
    def get_status(analysis_id):
        if analysis_id in AnalysisService.ANALYSIS:
            worker = AnalysisService.ANALYSIS[analysis_id]
            if type(worker) == LocalStreamingWorkFlowHandler:
                response = {
                    "workflow_status": worker.is_running(),
                    "sinking_status": worker.is_sinking(),
                    "streaming_status": worker.is_streaming()
                }  
            elif type(worker) == RemoteStreamingWorkflowHandler:
                response = {
                    "workflow_status": worker.is_running()
                }  
            return response,200
        else:
            return err_resp("Analysis not found!", "analysis_404", 404)
        
        