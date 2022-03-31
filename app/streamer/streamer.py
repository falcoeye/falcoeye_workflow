import threading
from app.io import source
import time

class StreamerWorker:
    def __init__(self,workflowWorker,sample_every,sink):
        self._workflowWorker = workflowWorker
        self._streamer = None
        self._sample_every = sample_every
        self._sink = sink
    
    def start(self):
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

class FileStreamWorker(StreamerWorker):
    def __init__(self,workflowWorker,filepath,sample_every,sink):
        StreamerWorker.__init__(self,workflowWorker,sample_every,sink)
        self._filepath = filepath 
    
    def start(self):
        self._streamer = source.create_file_streamer(self._filepath, 
            self._sample_every)
        return StreamerWorker.start(self)
    
    def stream(self):
        count = 0
        frame_num = 0
        total_frames = self._streamer.num_frames
        streamer = self._streamer
        while  frame_num < total_frames:
            hasFrame, frame = streamer.read()
            if not hasFrame:
                break
            self._sink.sink(frame_num,frame,count)
            frame_num += self._sample_every
            streamer.seek(frame_num)
            count += 1
        self._streamer.close()
        self.done_callback()

class WebStreamWorker(StreamerWorker):
    def __init__(self,workflowWorker,url,stream_provider,resolution,sample_every,length,sink):
        StreamerWorker.__init__(self,workflowWorker,sample_every,sink)
        self._url = url
        self._stream_provider = stream_provider
        self._resolution = resolution
        self._length = length

    def start(self):
        self._streamer = source.create_web_streamer(self._url, 
            self._stream_provider,
            self._resolution,
            self._sample_every,
            self._length)
        
        return StreamerWorker.start(self)
    
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
    

    

