
from app.node.node import Node
import json
import logging
import numpy as np
from .utils import get_color_from_number
from PIL import Image


class FalcoeyeDetection:
    def __init__(self,frame,detections, category_map):
        self._frame = frame
        self._detections = detections
        self._category_map = category_map
        self._boxes = [d["box"] for d in self._detections]
        self._classes = [d["class"] for d in self._detections]
    
    @property
    def size(self):
        return self._frame.size
    
    @property
    def frame(self):
        return self._frame.frame

    @property
    def frame_bgr(self):
        return self._frame.frame_bgr
    
    @property
    def count(self):
        return len(self._detections)
    
    @property
    def boxes(self):
        return self._boxes

    @property
    def classes(self):
        return self._classes

    @property
    def framestamp(self):
        return self._frame.framestamp
    
    @property
    def timestamp(self):
        return self._frame.timestamp

    def count_of(self, category):
        if category in self._category_map:
            return len(self._category_map[category])
        return -1

    def get_class_instances(self, name):
        return [i for i, d in enumerate(self._detections) if d["class"] == name]

    def get_class(self, i):
        return self._detections[i]["class"]

    def get_box(self, i):
        return self._detections[i]["box"]

    def detele(self,index):
        item = self.detections.pop(index)
        self._category_map[item["class"]] -= 1

    def save_frame(self,path):
        Image.fromarray(self._frame).save(f"{path}/{self._frame_number}.png")

    def __lt__(self,other):
        if type(other) == FalcoeyeDetection:
            return self._frame < other._frame
        else:
            # assuming other is FalcoeyeFrame
            return self._frame < other
    
    def __eq__(self,other):
        if type(other) == FalcoeyeDetection:
            return self._frame == other._frame
        else:
            # assuming other is FalcoeyeFrame or int
            return self._frame == other

class FalcoeyeDetectionNode(Node):
    
    def __init__(self, name, labelmap,min_score_thresh,max_boxes):
        Node.__init__(self,name)
        self._min_score_thresh = min_score_thresh
        self._max_boxes = max_boxes
        if type(labelmap) == str:
            with open(labelmap) as f:
                self._category_index = {int(k):v for k,v in json.load(f).items()}
        elif type(labelmap) == dict:
            self._category_index = {int(k):v for k,v in labelmap.items()}

    def translate(self,detections):
        _detections = []
        logging.info("Translating detection")
        _category_map = {k:[] for k in self._category_index.values()}
        _category_map["unknown"] = []

        if detections is None or type(detections) != dict or "detection_boxes" not in detections:
            return _detections, _category_map
        
        

        boxes = np.array(detections["detection_boxes"])
        classes = np.array(detections["detection_classes"]).astype(int)
        scores = np.array(detections["detection_scores"])
        
        logging.info(f"#boxes {boxes.shape}, #classes {classes.shape} #scores {scores.shape}")


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
        return _detections, _category_map

    def run(self,context=None):
        logging.info(f"Running falcoeye detection")
        while self.more():
            item = self.get()
            frame,raw_detections = item
            try:
                if type(raw_detections) == dict and "prediction" in raw_detections:
                    # restful
                    raw_detections = ['predictions'][0]
                elif raw_detections is None:
                    # TODO: should do failover
                    raw_detections = {'detection_boxes': np.array([]),
                    'detection_classes':np.array([]),
                    'detection_scores': np.array([])}
                else:
                    # gRPC response
                    logging.info("gRPC detection")
                    boxes = np.array(raw_detections.outputs['detection_boxes'].float_val).reshape((-1,4)).tolist()
                    classes = raw_detections.outputs['detection_classes'].float_val
                    scores = raw_detections.outputs['detection_scores'].float_val
                    raw_detections = {'detection_boxes': boxes,
                        'detection_classes':classes,
                        'detection_scores': scores}
                
                logging.info(f"New frame for falcoeye detection  {frame.framestamp} {frame.timestamp}")
                detections, category_map = self.translate(raw_detections)
                fe_detection = FalcoeyeDetection(frame,detections, 
                        category_map)
                self.sink(fe_detection)
            except Exception as e:
                logging.error(e)
    
