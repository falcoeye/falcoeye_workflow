import cv2
from PIL import Image
import socket

class Sink:
    def __init__(self):
        pass

    def open(self):
        pass

    def sink(self, frame):
        pass

    def close(self):
        pass


class VideoFileSink(Sink):
    def __init__(self, filename):
        Sink.__init__(self)
        self._filename = filename
        self._writer = None

    def open(self, frames_per_second, width, height):
        self._writer = cv2.VideoWriter(
            self._filename,
            fourcc=cv2.VideoWriter_fourcc(*"mp4v"),
            fps=float(frames_per_second),
            frameSize=(width, height),
            isColor=True,
        )

    def sink(self, frame):
        self._writer.write(frame)

    def close(self):
        self._writer.release()

class AISink(Sink):
    def __init__(self,analysis_id,modelHandler,wf_handler):
        self._analysis_id = analysis_id
        self._modelHandler = modelHandler
        self._wf_handler = wf_handler
    
    def sink(self,c_time,frame,count):
        data = {
            "analysis_id": self._analysis_id,
            "count": count,
            "init_time": c_time
        }
        print(data)
        # TODO: in async ways
        AISink.sink_(frame,data,self._modelHandler,self._wf_handler)
    @staticmethod
    def sink_(frame,data,model_handler,wf_handler):
        
        results_path =  model_handler.predict(frame,data)
        print("results received",results_path)
        wf_handler.put(results_path)

class ImageSink(Sink):
    def __init__(self, filename):
        Sink.__init__(self)
        self._filename = filename

    def open(self):
        pass

    def sink(self, frame):
        Image.fromarray(frame).save(self._filename)

    def close(self):
        pass

