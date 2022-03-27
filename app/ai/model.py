from app.utils import array_to_base64
from queue import Queue
import time
import threading
import hashlib
import config
from flask import current_app
import json
import requests
import numpy as np
import io
from PIL import Image

class FalcoeyeDetection:
    def __init__(self, detections, category_map):
        self._detections = detections
        self._category_map = category_map

    def count_of(self, category):
        if category in self._category_map:
            return len(self._category_map[category])
        return -1

    def get_boxes(self):
        return [d["box"] for d in self._detections]

    def get_class_instances(self, name):
        return [i for i, d in enumerate(self._detections) if d["class"] == name]

    def get_class(self, i):
        return self._detections[i]["class"]

    def get_classes(self):
        return [d["class"] for d in self._detections]

    def count(self):
        return len(self._detections)

    def get_box(self, i):
        return self._detections[i]["box"]


class FalcoeyeVideoDetection(FalcoeyeDetection):
    def __init__(self, detections, category_map, frame_number, relative_time):
        FalcoeyeDetection.__init__(self, detections, category_map)
        print(detections, category_map, frame_number, relative_time)
        self._frame_number = frame_number
        self._relative_time = relative_time

    def get_framestamp(self):
        return self._frame_number

    def get_timestamp(self):
        return self._relative_time


class ModelContainer:
    def __init__(self,server=None):
        self._server = server
        self._running = False
    
    def assign_new_server(self,server):
        self._server = server
    
    def run_new(self):
        self._server = "http://0.0.0.0:8000/predict/"
        self._running = True
        return True
    
    def isRunning(self):
        return self._running

    def send(self,frame,data):
        buf = io.BytesIO()
        Image.fromarray(frame).save(buf, format='PNG')
        buf.seek(0)
        response = requests.post(f"{self._server}",params=data,files=[('frame', buf)]).text.replace("\"","")

        return response

class ModelHandler:
    _handlers = {}
    def __init__(self,name,task,framework,base_arch,size,deployment_type,deployment_path):
        self._name = name
        self._task = task
        self._framework = framework
        self._base_arch = base_arch
        self._size = size
        self._deployment_type = deployment_type
        self._deployment_path = deployment_path
        
        self._container = ModelContainer()

    def run(self):
        if self._container.isRunning():
            return True
        didRun =  self._container.run_new()
        return didRun
    
    def isRunning(self):
        return self._container.isRunning()
    
    def predict(self,frame,data):
        response = self._container.send(frame,data)
        return response

    @staticmethod
    def init(model_data):
        model_name = model_data["name"] 
        if model_name in ModelHandler._handlers:
            return ModelHandler._handlers[model_name]
        else:
            handler = ModelHandler(**model_data)
            ModelHandler._handlers[model_name] = handler
            return handler

   