import threading
import requests
import numpy as np
import io
from PIL import Image

class ModelContainer:
    def __init__(self,server=None):
        self._server = server
        self._running = False
    
    def assign_new_server(self,server):
        self._server = server
    
    def start(self):
        self._server = "http://0.0.0.0:8000/predict/"
        self._running = True
        return True
    
    def is_running(self):
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

    def start(self):
        if self._container.is_running():
            return True
        didRun =  self._container.start()
        return didRun
    
    def is_running(self):
        return self._container.is_running()
    
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

   