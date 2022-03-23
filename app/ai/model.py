from .utils import image_to_base64,mkdir,randome_string
from queue import Queue
import time
import threading
import hashlib
import config
from flask import current_app
import json

class ModelContainer:
    def __init__(self,server=None):
        self._server = server
        self._running = False
    
    def assign_new_server(self,server):
        self._server = server
    
    def run_new(self):
        self._server = 0 # run here
    
    def isRunning(self):
        return self._running

    def send(self,item):
        pass

class ModelHandler:
    self._handlers = {}
    def __init__(self,name,task,framework,base_arch,size,deployment_type,deployment_path):
        self._name = name
        self._task = task
        self._framework = framework
        self._base_arch = base_arch
        self._size = size
        self._deployment_type = deployment_type
        self._deployment_path = path
        
        self._container = ModelContainer()

    def run(self):
        if self._container.isRunning():
            return True
        didRun =  self._container.run_new()
        return didRun
    
    def isRunning(self):
        return self._container.isRunning()
    
    def predict(self,item):
        self._container.send(item)

    @staticmethod
    def init(model_data):
        model_name = model_data["name"] 
        if model_name in ModelHandler._handlers[model_name]:
            return ModelHandler._handlers[model_name]
        else:
            handler = ModelHandler(**model_data)
            ModelHandler._handlers[model_name] = handler
            return handler

   