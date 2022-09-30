
from app.node.node import Node
import logging
import cv2
import numpy as np
import datetime

class Source(Node):
    def __init__(self,name,**kwargs):
        Node.__init__(self,name)

    def open(self):
        pass

    def read(self):
        pass

    def close(self):
        pass


class FalcoeyeFrame:
    def __init__(self,frame,frame_number,relative_time,time_unit):
        #logging.info(f"New FalcoeyeFrame {frame_number} {relative_time}")
        self._frame = frame.astype(np.uint8)
        self._frame_number = frame_number
        self._relative_time = relative_time
        self._frame_bgr = cv2.cvtColor(self._frame, cv2.COLOR_RGB2BGR)
        self._time_unit = time_unit
    
    @property
    def size(self):
        return self._frame.shape

    @property
    def frame(self):
        return self._frame

    @property
    def frame_bgr(self):
        return self._frame_bgr
    

    @property
    def framestamp(self):
        return self._frame_number
    
    @property
    def timestamp(self):
        if self._time_unit == "frame":
            return self._relative_time
        elif self._time_unit == "epoch":
           return datetime.datetime.fromtimestamp(self._relative_time)
    
    def __lt__(self,other):
        return self._frame_number < other.framestamp
    
    def __eq__(self,other):
        if type(other) == FalcoeyeFrame:
            return self._frame_number == other.framestamp
        elif type(other) == int:
            return self._frame_number == other