import threading
import requests
import numpy as np
import io
from PIL import Image
from datetime import datetime
import asyncio
import logging
from object_detection.utils import config_util, label_map_util
from app.ai.utils import get_color_from_number
import six
import json 
_handlers = {}

class FalcoeyeContainer:
    def __init__(self,server=None):
        self._server = server
        self._running = False
    
    def assign_new_server(self,server):
        self._server = server
    
    def start(self):
        self._server = "http://0.0.0.0:8000/predict"
        self._running = True
        return True
    
    def is_running(self):
        return self._running

    def send(self,frame,data):
        logging.info("Packaging data")
        buf = io.BytesIO()
        Image.fromarray(frame).save(buf, format='PNG')
        buf.seek(0)
        logging.info("Sending package")
        response = requests.post(f"{self._server}",params=data,files=[('frame', buf)]).text.replace("\"","")

        return response
    
    async def send_async(self,session,frame,data):
        logging.info(data)
        logging.info("Packaging data")
        try:
            buf = io.BytesIO()
            img = Image.fromarray(frame)
            img.save(buf, format='PNG')
            buf.seek(0)
            logging.info("Sending package")
            async with session.post(self._server,params=data,data={'frame': buf}) as response:
                logging.info("waiting for response")
                respath = await response.text()
                respath = respath.replace("\"","")         
                logging.info(respath)
                self._wf_handler.put(respath)
            img.close()
            return respath
        except Exception as e:
            logging.error(e)
        

class TensorflowServingContainer:
    def __init__(self,path,server=None,
        model_name=None,
        model_version=1,
        min_score_thresh=0.5,
        max_boxes=20):
        self._path = path
        self._server = server
        self._predict_url = f"{self._server}/v{model_version}/models/{model_name}:predict"
        self._running = False
        self._category_index = label_map_util.create_category_index_from_labelmap(
            f"{self._path}/label_map.pbtxt", use_display_name=True
        )
        self._min_score_thresh = min_score_thresh
        self._max_boxes = max_boxes
    
    def assign_new_server(self,server):
        self._server = server
    
    def start(self):
        self._running = True
        return True
    
    def is_running(self):
        return self._running

    
    def translate(self,detections):
        
        _detections = []

        _category_map = {k["name"]: [] for k in list(self._category_index.values())}
        _category_map["unknown"] = []
        boxes = np.array(detections["detection_boxes"])
        classes = np.array(detections["detection_classes"]).astype(int)
        scores = np.array(detections["detection_scores"])
  
        counter = 0
        for i in range(boxes.shape[0]):
            if self._max_boxes == len(_detections):
                break
            if scores is None or scores[i] > self._min_score_thresh:
                box = tuple(boxes[i].tolist())
                if classes[i] in six.viewkeys(self._category_index):
                    class_name = str(self._category_index[classes[i]]["name"])
                else:
                    class_name = "unknown"
                color = get_color_from_number(classes[i])
                _detections.append(
                    {
                        "box": box,
                        "color": color,
                        "class": class_name,
                        "score": round(scores[i], 2) * 100,
                    }
                )
                _category_map[class_name].append(counter)
                counter += 1
        return _detections, _category_map

    def send(self,frame,meta_data):
        data = json.dumps({"signature_name": "serving_default", "instances": [frame.tolist()]})
        headers = {"content-type": "application/json"}
        response = requests.post(self._predict_url, data=data, headers=headers)
        predictions = json.loads(response.text)['predictions'][0]
        detections,category_map = self.translate(predictions)
        results = {"detection": detections,"category_map": category_map,
                    "init_time":meta_data["init_time"],"count": meta_data["count"]}
        return results

    async def send_async(self,session,frame,meta_data):
        try:
            data = json.dumps({"signature_name": "serving_default", "instances": [frame.tolist()]})
            headers = {"content-type": "application/json"}
            logging.info(meta_data)
            async with session.post(self._predict_url,data=data,headers=headers) as response:
                logging.info("waiting for response")
                responseText = await response.text()
                predictions = json.loads(responseText)['predictions'][0]
                detections,category_map = self.translate(predictions)
                results = {"detection": detections,"category_map": category_map,
                            "init_time":meta_data["init_time"],"count": meta_data["count"]}
                return results
        except Exception as e:
            logging.error(e)
        

class ModelHandler:
    
    def __init__(self,name,task,framework,base_arch,size,deployment_type,deployment_path,container,version=1):
        self._name = name
        self._task = task
        self._framework = framework
        self._base_arch = base_arch
        self._size = size
        self._deployment_type = deployment_type
        self._deployment_path = deployment_path
        self._version = version
        self._container = container


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
    
    async def predict_async(self,session,frame,data):
        response = await self._container.send_async(session,frame,data)
        return response


def create_model_handler(model_data,model_server="falcoeye"):
    global _handlers
    model_name = model_data["name"] 
    if model_name in _handlers:
        return _handlers[model_name]
    else:
        if model_server == "falcoeye":
            container = FalcoeyeContainer()
            model_data["container"] = container
        elif model_server == "tfserving":
            model_path = model_data["deployment_path"]
            model_name = model_data["name"]
            server = "http://localhost:8501"
            container = TensorflowServingContainer(model_path,server,model_name)
            model_data["container"] = container

        handler = ModelHandler(**model_data)
        _handlers[model_name] = handler
        return handler