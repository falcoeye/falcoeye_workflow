from falcoeye_core.workflow import ObjectDetectionWorkflow
import json
from PIL import Image
import numpy as np
from queue import Queue


class DataFetcher:
    def __init__(self):
        pass
    def fetch(self):
        pass

class LocalDataFetcher(DataFetcher):
    def __init__(self):
        DataFetcher.__init__(self)
    
    def fetch(self,data):
      
        framePath = data["frame"]
        resultsPath = data["results"]  
        img = Image.open(framePath)
        frame = np.asarray(img).copy()
        img.close()
        with open(resultsPath) as f2:
            results = json.load(f2)
        return frame,results

class WorkflowHandler: 
     def __init__(self,analysis_id,workflow_dict,workflow_args):
        self._analysis_id = analysis_id
        w = ObjectDetectionWorkflow()
        w._args = workflow_dict["input_args"]

        w.load_calculations(workflow_dict["calculations"])
        w.load_outputters(workflow_dict["outputters"])
        w.fill_args(workflow_args)
        self._model = workflow_dict["model"]
        self._datafetcher = LocalDataFetcher()
        self._w = w
        

    def fill_args(self,data):
        self._w.fill_args(data)


class LocalStreamingWorkflowHandler:
    def __init__(self,analysis_id,workflow_dict,workflow_args):
        WorkflowHandler.__init__(self,analysis_id,workflow_dict,workflow_args)
        self._still = False
        self._queue = Queue()

    def put(self,results):
        self._queue.put(results)

    def done_streaming(self):
        self._still = False

    def fetch_results(self):
        resultsData = self._queue.get()
        frame,results = self._datafetcher.fetch(resultsData)
        return frame,results

    def start(self):
        self._still = True
        b_thread = threading.Thread(
                target=WorkflowHandler.start_calculator,
                args=self,
            )
        b_thread.start()

    def more(self):
        return self._queue.qsize() > 0
    
    @classmethod
    def start_calculator(handler):
        while handler._still or handler.more():
            if handler.more():
                frame,results = handler.fetch_results()
                handler._w.calculate_on_prediction(frame, results)
        handler._w.calculate_on_calculation()
        handler._w.output()


class WorkflowFactory:
    Factory = None
    def __init__(self,portofolio):
        self._workflows = json.load(portofolio)
    
    @staticmethod
    def create(analysis_id,workflow):
        workflow_name = workflow["name"]
        workflow_args = workflow["args"]
        workflow_dict = self._workflows[workflow_name]
        w = LocalStreamingWorkflowHandler(analysis_id,workflow_dict,workflow_args)
        return w
        


    