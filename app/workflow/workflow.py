import json
import numpy as np
import threading
from queue import Queue
from app.io import csv as csv
from app.io import video as video
from app.ai.detection import FalcoeyeVideoDetection
from app.utils import check_type
from .calculation import *
from .outputter import CalculationOutputter
from datetime import datetime
import requests
import glob 
import logging



class Workflow:
    def __init__(self):
        self._name = None
        self._model = None
        self._model_arch = None
        self._args = []
        self._calculations = {}
        self._outputters = []
        self._resources = {}

    def calculate(self, results):
        pass

    def output(self):
        pass

    def load_args(self, args):
        pass

    def load_calculations(self):
        pass

    def start(self):
        pass

    def interpret(self, d):
        for k, v in d.items():
            if v is not None and type(v) == str and v[0] == "$":
                try:
                    d[k] = self._resources[v[1:]]
                except KeyError as e:
                    logging.info(f"Interpretation error: couldn't interpret {v} in {k}")
                    exit(0)
        return d
        
class ObjectDetectionWorkflow(Workflow):
    def __init__(self):
        Workflow.__init__(self)
        self._calculations = {}
        self._prediction_calculation = []
        self._calculation_calculations = []

    def fill_args(self, args):
        for a in self._args:
            atype = a["type"]
            aname = a["name"]
            adefault = a.get("default", None)
            required = a.get("required", False)
            if adefault is None and required and aname not in args:
                logging.error(
                    f"Error: You must provide a valid {aname} for the workflow to start"
                )
                exit()

            if aname in args:
                v = args[aname]
                if not check_type(v, atype) and v is not None:
                    vc = try_cast(v, atype)
                    if not vc:
                        logging.error(
                            f"Error: Type of {aname} != {atype} and neither can be casted to it"
                        )
                        exit()
                self._resources[aname] = args[aname]
            elif adefault:
                self._resources[aname] = adefaul

    def load_calculations(self, cal_list):
        self._calculations = {}
        self._prediction_calculation = []
        self._calculation_calculations = []

        cal_types = {
            "record_timestamp": TimestampRecorder,
            "type_counter": TypeCounter,
            "put_on_pd": CalculationsToDf,
            "record_frames": FramesRecorder,
            "record_detections": DetectionRecorder,
            "zone_filter": ZoneFilter,
            "type_filter": TypeFilter,
            "and_filters": AndFilters,
            "visualize_detection_on_frames": VisualizeDetectionOnFrames,
            "visualize_zone_on_frames": VisualizeZoneOnFrames,
            "dection_of_filter": DetectionOfFilter,
            "object_monitor": ObjectMonitor,
        }
        for c in cal_list:
            cname = c["name"]
            ctype = c["type"]

            if c["on"] == "prediction":
                self._prediction_calculation.append(cname)
            elif c["on"] == "calculation":
                self._calculation_calculations.append(cname)
            c = self.interpret(c)
            self._calculations[cname] = cal_types[ctype].create(**c)

    def load_outputters(self, outputter_list):
        io_handler_types = {
            "csv": csv.CSVWriter,
            "video": video.VideoWriter,
            "multivideos": video.MultiVideosWriter,
        }
        for outputter in outputter_list:
            outputter = self.interpret(outputter)

            oname = outputter["name"]
            io_handler_type = outputter["io_handler"]
            io_handler = io_handler_types[io_handler_type].create(**outputter)
            on = outputter["on"]

            if on == "calculation":
                calculation = self._calculations[outputter["calculation"]]
                self._outputters.append(
                    CalculationOutputter(oname, io_handler, calculation)
                )

    def calculate_on_prediction(self, frame, results):
        for c in self._prediction_calculation:
            self._calculations[c](frame, results)

    def calculate_on_calculation(self):
        for c in self._calculation_calculations:
            cobject = self._calculations[c]
            cals = [self._calculations[ck] for ck in cobject.keys()]
            self._calculations[c](cals)

    def output(self):
        for o in self._outputters:
            o.run()

class WorkflowHandler:
    def __init__(self,analysis_id,workflow_structure,workflow_args,prediction_fetcher):
        self._analysis_id = analysis_id
        self._w = ObjectDetectionWorkflow()
        self._w._args = workflow_structure["input_args"]
        self._w.fill_args(workflow_args)
        self._w.load_calculations(workflow_structure["calculations"])
        self._w.load_outputters(workflow_structure["outputters"])
        
        self._model = workflow_structure["model"]
        self._prediction_fetcher = prediction_fetcher
        self._running = False

    def fill_args(self,data):
        self._w.fill_args(data)
    
    def is_running(self):
        return self._running
    
    def start(self):
        b_thread = threading.Thread(
                target=self.start_calculator_,
                args=(),
            )
        b_thread.daemon = True
    
        b_thread.start()
        self._running = True
        return b_thread.is_alive()
    
    def done_(self):
        self._running = False
        # TODO: postback to backend
        pass

class LocalStreamingWorkFlowHandler(WorkflowHandler):
    def __init__(self,analysis_id,workflow_structure,workflow_args,prediction_fetcher):
        WorkflowHandler.__init__(self,analysis_id,workflow_structure,workflow_args,prediction_fetcher)
        self._still_streaming = False
        self._still_sinking = False
        self._queue = Queue()
        
    
    def more(self):
        return self._queue.qsize() > 0

    def put(self,results):
        self._queue.put(results)

    def fetch_results(self):
        resultsPath = self._queue.get()
        frame,results = self._prediction_fetcher.fetch(resultsPath)
        return frame,results

    def start(self):
        self._still_streaming = True
        self._still_sinking = True
        b_thread = threading.Thread(
                target=self.start_calculator_,
                args=(),
            )
        b_thread.daemon = True
    
        b_thread.start()
        self._running = True
        return b_thread.is_alive()

    def is_sinking(self):
        return self._still_sinking

    def is_streaming(self):
        return self._still_streaming

    def done_streaming(self):
        self._still_streaming = False
    
    def done_sinking(self):
        self._still_sinking = False
    
    def start_calculator_(self):
        while self._still_streaming or self._still_sinking or self.more():
            if self.more():
                logging.info("New results calculating")
                frame,results = self.fetch_results()
                falcoeye_detection = FalcoeyeVideoDetection(
                    results["detection"], results["category_map"], 
                    results["count"], results["init_time"]
                )
                self._w.calculate_on_prediction(frame, falcoeye_detection)
        self._w.calculate_on_calculation()
        self._w.output()
        self.done_()

class RemoteStreamingWorkflowHandler(WorkflowHandler):
    def __init__(self,analysis_id,workflow_structure,workflow_args,prediction_fetcher,**args):
        WorkflowHandler.__init__(self,analysis_id,workflow_structure,workflow_args,prediction_fetcher)
        self._server = "http://0.0.0.0:8000"
        self._stream_extensions = {
            "file": "predict_file",
            "stream": "predict_webstream"
        }
        self._stream_args = args
        # because the AI container would require this for any post
        self._stream_args["analysis_id"] = analysis_id

    def fetch_results(self,resultsPath):
        for rp in sorted(glob.glob(f"{resultsPath}/*")):
            frame,results = self._prediction_fetcher.fetch(rp)
            yield frame, results
    
    def start_calculator_(self):
        stream_type = self._stream_args["type"]
        stream_extension = self._stream_extensions[stream_type]
        response = requests.post(f'{self._server}/{stream_extension}',
            params=self._stream_args)
        resultsPath = response.text.replace("\"","")

        logging.info("Start calculating")
        for frame,results in self.fetch_results(resultsPath):
            falcoeye_detection = FalcoeyeVideoDetection(
                results["detection"], results["category_map"], 
                results["count"], results["init_time"]
            )
            self._w.calculate_on_prediction(frame, falcoeye_detection)

        self._w.calculate_on_calculation()
        self._w.output()
        self.done_()

class WorkflowFactory:
    def __init__(self):
        pass

    @staticmethod
    def create(analysis_id,workflow_structure,workflow_args,streaming,prediction_fetcher,**args):
        if streaming == "local":
            w = LocalStreamingWorkFlowHandler(analysis_id,workflow_structure,workflow_args,prediction_fetcher)
        elif streaming == "remote":
            w = RemoteStreamingWorkflowHandler(analysis_id,workflow_structure,workflow_args,prediction_fetcher,**args)
        else:
            raise NotImplementedError

        return w