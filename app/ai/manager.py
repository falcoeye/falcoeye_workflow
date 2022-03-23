from .model import ModelHandler
import os
import json


class ModelManager:
    singlton = None
    def __init__(self):
        self._models = {}

    def predict_item(self,model_name,item):
        if handler := ModelManager.singlton.get_model(model_name):
            handler.predict(item)
            return True
        # TODO jalalirs: What to do here?
        return False
    
    def add_model(self,modelHandler):
        self._models[modelHandler.name] = modelHandler

    def get_model(self,modelname):
        if modelname in self._models:
            return self._models[modelname]
        return None

    @staticmethod
    def predict(model_name,item):
        return ModelManager.singlton.predict_item(model_name,item)

    @staticmethod
    def run(model_data):
        model_name = model_data["name"] 
        if (handler := ModelManager.singlton.get_model(model_name)):
            return handler
        else:
            handler = ModelHandler(**model_data)
            ModelManager.singlton.add_model(handler)
            return handler

    
    @staticmethod
    def init(model_repo):
        ModelManager.singlton = ModelManager(model_repo)

