import json
from PIL import Image
import numpy as np
import threading
from queue import Queue
from app.io import csv as csv
from app.io import video as video
from app.io.storage import LocalStorageDataFetcher
from app.ai.model import FalcoeyeVideoDetection
from app.utils import check_type
from .calculation import *
from .outputter import CalculationOutputter

class AnalysisBank:
    singlton = None
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
    def init():
        AnalysisBank.singlton = AnalysisBank()

    @staticmethod
    def register(aid,worker):
        AnalysisBank.singlton.register_(aid,worker)

    @staticmethod
    def put(aid,item):
        AnalysisBank.singlton.put_(aid,item)

    @staticmethod
    def done_streaming(aid):
        AnalysisBank.singlton.done_streaming_(aid)
    
    @staticmethod
    def done_workflow(aid):
        AnalysisBank.singlton.done_workflow_(aid)

    @staticmethod
    def get_status(aid):
        if aid in AnalysisBank.singlton._running:
            return "running"
        else:
            return "done"


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

    def run(self):
        pass

    def interpret(self, d):
        for k, v in d.items():
            if v is not None and type(v) == str and v[0] == "$":
                try:
                    d[k] = self._resources[v[1:]]
                except KeyError as e:
                    print(f"Interpretation error: couldn't interpret {v} in {k}")
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
            print(a)
            atype = a["type"]
            aname = a["name"]
            adefault = a.get("default", None)
            required = a.get("required", False)
            if adefault is None and required and aname not in args:
                print(
                    f"Error: You must provide a valid {aname} for the workflow to start"
                )
                exit()

            if aname in args:
                v = args[aname]
                if not check_type(v, atype) and v is not None:
                    vc = try_cast(v, atype)
                    if not vc:
                        print(
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
            print(c)
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
    def __init__(self,analysis_id,workflow_dict,workflow_args):
        self._analysis_id = analysis_id
        self._w = ObjectDetectionWorkflow()
        self._w._args = workflow_dict["input_args"]
        print(workflow_args)
        self._w.fill_args(workflow_args)
        self._w.load_calculations(workflow_dict["calculations"])
        self._w.load_outputters(workflow_dict["outputters"])
        
        self._model = workflow_dict["model"]
        self._datafetcher = LocalStorageDataFetcher()
        
        self._still = False
        self._queue = Queue()
        self._done_callback = None

    def fill_args(self,data):
        self._w.fill_args(data)
    
    def put(self,results):
        self._queue.put(results)

    def done_streaming(self):
        self._still = False

    def fetch_results(self):
        resultsPath = self._queue.get()
        frame,results = self._datafetcher.fetch(resultsPath)
        return frame,results

    def start(self,callback):
        self._done_callback = callback
        self._still = True
        b_thread = threading.Thread(
                target=self.start_calculator_,
                args=(),
            )
        b_thread.daemon = True
    
        b_thread.start()
    
    def done_callback(self):
        self._done_callback(self._analysis_id)

    def more(self):
        return self._queue.qsize() > 0
    
    def start_calculator_(self):
        while self._still or self.more():
            if self.more():
                frame,results = self.fetch_results()
                print(results)
                falcoeye_detection = FalcoeyeVideoDetection(
                    results["detection"], results["category_map"], 
                    results["count"], results["init_time"]
                )
                print(falcoeye_detection)
                self._w.calculate_on_prediction(frame, falcoeye_detection)
                print("Calculation done")
        print("Finished calculator",flush=True)
        self._w.calculate_on_calculation()
        self._w.output()
        self.done_callback()

class WorkflowFactory:
    Factory = None
    def __init__(self,portofolio):
        with open(portofolio) as f:
            self._workflows = json.load(f)
    
    @staticmethod
    def init(portofolio):
        # TODO: from db
        WorkflowFactory.Factory = WorkflowFactory(portofolio)

    @staticmethod
    def create(analysis_id,workflow):
        workflow_name = workflow["name"]
        workflow_args = workflow["args"]
        workflow_dict = WorkflowFactory.Factory._workflows[workflow_name]
        w = WorkflowHandler(analysis_id,workflow_dict,workflow_args)
        return w
        


    