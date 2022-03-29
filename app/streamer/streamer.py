import threading
from app.io import source
import time

class WebStreamWorker:
    def __init__(self,analysis_id,url,stream_provider,resolution,sample_every,length,sink):
        self._analysis_id = analysis_id
        self._url = url
        self._stream_provider = stream_provider
        self._resolution = resolution
        self._sample_every = sample_every
        self._length = length
        self._sink = sink
        self._streamer = None
        self._done_callback = None

    def start(self,callback):
        self._done_callback = callback
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
        self._sink.close()
        self._done_callback(self._analysis_id)

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
        print("done streaming")
        self.done_callback()
    

    

