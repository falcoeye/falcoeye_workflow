from threading import Thread
import cv2
import numpy

from .source import Source

class VideoFileSource(Source):
    def __init__(self, name, filename,sample_every):
        Source.__init__(self,name)
        self._filename = filename
        self._sample_every = sample_every
        self._reader = None
        self.width = -1
        self.height = -1
        self.frames_per_second = -1
        self.num_frames = -1

    def open(self):
        self._reader = cv2.VideoCapture(self._filename)
        self.width = int(self._reader.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self._reader.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frames_per_second = self._reader.get(cv2.CAP_PROP_FPS)
        self.num_frames = int(self._reader.get(cv2.CAP_PROP_FRAME_COUNT))

    def seek(self,n):
        self._reader.set(cv2.CAP_PROP_POS_FRAMES,n)

    def run(self):
        self.open()
        counter = 0
        count = 0
        while counter < self.num_frames:
            hasFrame, frame = self._reader.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if not hasFrame:
                break
            for sink in self._sinks:
                self.sink((counter,count,frame))
            count += 1
            counter += self._sample_every
            self.seek(self._sample_every)
        
    def run_async(self):
        self.open()
        self._thread = Thread(target=self.run, args=(),daemon=True)
        self._thread.start()

    def close(self):
        self._reader.release()
        self.width = -1
        self.height = -1
        self.frames_per_second = -1
        self.num_frames = -1
    

