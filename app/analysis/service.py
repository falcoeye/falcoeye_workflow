import dateutil.parser
from flask import current_app

from app import db
from app.utils import err_resp, internal_err_resp, message
from streamer import WebStreamWorker,Sink
from factory import WorkflowFactory


class AnalysisBank:
    singlton = AnalysisBank()
    def __init__(self):
        self._running = {}
    
    def register_(self,aid,worker):
        self._running[aid] = worker
    
    def put_(self,aid,item):
        self._running[aid].put(item)
    
    def done_streaming_(self,aid):
        self._running[aid].done_streaming()
    
    def done_workflow_(self,aid):
        del self._running[aid]
    
    @staticmethod
    def register(aid,worker):
        AnalysisBank.singlton.register(aid,worker)

    @staticmethod
    def put(aid,item):
        AnalysisBank.singlton.put(aid,item)

    @staticmethod
    def done_streaming(aid):
        AnalysisBank.singlton.done_streaming_(aid)
    
    @staticmethod
    def done_workflow(aid):
        AnalysisBank.singlton.done_workflow_(aid)


class AnalysisService:
    AnalysisBank = {}
    @staticmethod
    def new_analysis(data):
        stream = data["stream"]
        workflow = data["workflow"]
        stream_type = stream["type"]
        analysis_id = data["analysis"]["id"]
        sink = Sink(analysis_id)
        if stream_type == "file":
            pass
        elif stream_type == "stream":
            url = stream["url"]
            provider = stream["provider"]
            resolution = stream["resolution"]
            sample_every = stream.get("sample_every",1)
            length = stream.get("length",60)
            streamWorker = WebStreamWorker(analysis_id,url,provider,resolution,sample_every,length,sink)
            workflowWorker = WorkflowFactory.create(analysis_id,workflow)
        
        if not streamWorker.initialize():
            return internal_err_resp()
        
        if not workflowWorker.initialize():
            return internal_err_resp()

        AnalysisBank.register(analysis_id,workflowWorker)

        streamWorker.start(AnalysisService.done_streaming)
        workflowWorker.start(AnalysisService.done_workflow)
        resp = message(True, "Analysis started")
        return resp, 200

        except Exception as error:
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