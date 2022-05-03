from threading import Thread
import cv2
import numpy

from .source import Source
import logging

class VideoFileSource(Source):
    def __init__(self, name, filename,sample_every,length=-1):
        Source.__init__(self,name)
        self._filename = filename
        self._sample_every = sample_every
        self._num_frames = length
        self._frames_per_second = -1
        self._reader = None
        self.width = -1
        self.height = -1

    def open(self):
        self._reader = cv2.VideoCapture(self._filename)
        self.width = int(self._reader.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self._reader.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._frames_per_second = self._reader.get(cv2.CAP_PROP_FPS)
        if self._num_frames < 0:
            self._num_frames = int(self._reader.get(cv2.CAP_PROP_FRAME_COUNT))

    def seek(self,n):
        self._reader.set(cv2.CAP_PROP_POS_FRAMES,n)

    def run(self):
        self.open()
        counter = 0
        count = 0
        logging.info(f"Start streaming from {self._filename}")
        while counter < self._num_frames:
            hasFrame, frame = self._reader.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if not hasFrame:
                break
            logging.info(f"Frame {counter}/{self._num_frames}")
            for sink in self._sinks:
                self.sink((counter,count,frame))
            count += 1
            counter += self._sample_every
            self.seek(self._sample_every)
        logging.info(f"Streaming completed")
        if self._done_callback:
            self._done_callback(self._name)
        
        self.close()
        self.close_sinks()

    def run_async(self,done_callback):
        self._done_callback = done_callback
        self.open()
        self._thread = Thread(target=self.run, args=(),daemon=True)
        self._thread.start()

    def close(self):
        self._reader.release()
    
