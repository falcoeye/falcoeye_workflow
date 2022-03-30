import threading
from app.io import source
import time

class WebStreamWorker:
    def __init__(self,workflowWorker,url,stream_provider,resolution,sample_every,length,sink):
        self._workflowWorker = workflowWorker
        self._url = url
        self._stream_provider = stream_provider
        self._resolution = resolution
        self._sample_every = sample_every
        self._length = length
        self._sink = sink
        self._streamer = None

    def start(self):
        self._streamer = source.create_streamer(self._url, 
            self._stream_provider,
            self._resolution,
            self._sample_every,
            self._length)
        
        self._streamer.open()
        b_thread = threading.Thread(
                target=self.stream,
                args=(),
        )
        b_thread.daemon = True
        b_thread.start()
        
        return b_thread.is_alive()
   
    def done_callback(self):
        self._workflowWorker.done_streaming()
        self._sink.close()

    def stream(self):
        count = 0
        t_end = time.time() + self._length
        streamer = self._streamer
        c_time = time.time()
        while  c_time < t_end:
            hasFrame, frame = streamer.read()
            if not hasFrame:
                break
            self._sink.sink(c_time,frame,count)
            count += 1
            time.sleep(self._sample_every)
            c_time = time.time()

        self.done_callback()
    

    

