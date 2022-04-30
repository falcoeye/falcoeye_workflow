
from app.node.node import Node
from app.k8s import start_tfserving_container
import json
import logging
import numpy as np
from .utils import get_color_from_number
from PIL import Image
class FalcoeyeDetection:
    def __init__(self,frame,detections, category_map,frame_number, relative_time):
        self._frame = frame
        self._detections = detections
        self._category_map = category_map
        self._frame_number = frame_number
        self._relative_time = relative_time

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

    def get_framestamp(self):
        return self._frame_number

    def get_timestamp(self):
        return self._relative_time
    
    def detele(self,index):
        item = self.detections.pop(index)
        self._category_map[item["class"]] -= 1

    def save_frame(self,path):
        Image.fromarray(self._frame).save(f"{path}/{self._frame_number}.png")

class FalcoeyeDetectionNode(Node):
    def __init__(self, name, labelmap,min_score_thresh,max_boxes):
        Node.__init__(self,name)
        self._min_score_thresh = min_score_thresh
        self._max_boxes = max_boxes
        with open(labelmap) as f:
            self._category_index = {int(k):v for k,v in json.load(f).items()}

    def translate(self,detections):
        _detections = []

        _category_map = {k:[] for k in self._category_index.values()}
        _category_map["unknown"] = []
        boxes = np.array(detections["detection_boxes"])
        classes = np.array(detections["detection_classes"]).astype(int)
        scores = np.array(detections["detection_scores"])

        print(classes)
        counter = 0
        for i in range(boxes.shape[0]):
            if self._max_boxes == len(_detections):
                break
            if scores is None or scores[i] > self._min_score_thresh:
                box = tuple(boxes[i].tolist())
                if classes[i] in self._category_index:
                    class_name = str(self._category_index[classes[i]])
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
        logging.info(_detections)
        return _detections, _category_map

    def run(self):
        while self.more():
            item = self.get()
            init_time, frame_count, frame,raw_detections = item 
            detections, category_map = self.translate(raw_detections)
            fe_detection = FalcoeyeDetection(frame,detections, 
                    category_map, 
                    frame_count, 
                    init_time)
            self.sink(fe_detection)
    
    def run_async(self):
        pass

class TFObjectDetectionModel(Node):
    def __init__(self, name,
        model_name,
        version
        ):
        Node.__init__(self,name)
        self._model_name = model_name
        self._version = version
        self._container = None
        
    def run(self):
        logging.info(f"Starting tfserving container")
        self._container = start_tfserving_container(self._model_name,self._version)
        logging.info(f"Container started. Prediction path: {self._container._server}")
        while self.more():
            item = self.get()
            init_time, frame_count, frame = item 
            logging.info(f"New frame to post to container {init_time} {frame_count}")
            raw_detections =  self._container.post(frame)
            logging.info(f"Prediction received {frame_count}")
            self.sink([init_time,frame_count,frame,raw_detections])
        
        logging.info(f"{self._name} completed")
    
    def run_async(self):
        pass

    