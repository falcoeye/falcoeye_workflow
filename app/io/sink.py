import cv2
from PIL import Image
import socket
from queue import Queue
import threading

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
        self._queue = Queue()
        self._still = False
    
    def sink(self,c_time,frame,count):
        data = {
            "analysis_id": self._analysis_id,
            "count": count,
            "init_time": c_time
        }
        self._queue.put([frame,data])
        
    def more(self):
        return self._queue.qsize() > 0
        
    def close(self):
        self._still = False

    def start(self):
        self._still = True
        b_thread = threading.Thread(
                target=self.start_,
                args=(),
        )
        b_thread.daemon = True
        b_thread.start()
        return b_thread.is_alive()
  
    def start_(self):
        while self._still or self.more():
            if self.more():
                frame,data = self._queue.get()
                results_path =  self._modelHandler.predict(frame,data)
                self._wf_handler.put(results_path)
        self._wf_handler.done_sinking()
        

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

