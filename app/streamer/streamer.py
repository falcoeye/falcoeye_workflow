import threading
from app.io import source
import time
import logging

class StreamerWorker:
    def __init__(self,workflowWorker,sink,sample_every):
        self._workflowWorker = workflowWorker
        self._streamer = None
        self._sink = sink
        self._sample_every = sample_every
    
    def start(self):
        self._streamer.open()
        b_thread = threading.Thread(
                target=self.stream,
                args=(),
        )
        b_thread.daemon = True
        b_thread.start()
        logging.info(f"Streaming thread started? {b_thread.is_alive()}")
        return b_thread.is_alive()
    
    def done_callback(self):
        self._workflowWorker.done_streaming()
        self._sink.close()

class FileStreamWorker(StreamerWorker):
    def __init__(self,workflowWorker,filepath,sink,sample_every):
        StreamerWorker.__init__(self,workflowWorker,sink,sample_every)
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
        logging.info(f"Entering stream loop {frame_num}")
        while  frame_num < total_frames:
            hasFrame, frame = streamer.read()
            if not hasFrame:
                break
            logging.info(f"New frame fetched {count} {frame_num}")
            self._sink.sink(frame_num,frame,count)
            frame_num += self._sample_every
            streamer.seek(frame_num)
            count += 1
        logging.info(f"Exiting stream loop {frame_num}")
        self._streamer.close()
        self.done_callback()

class WebStreamWorker(StreamerWorker):
    def __init__(self,workflowWorker,sink,**streamer_args):
        StreamerWorker.__init__(self,workflowWorker,sink,streamer_args["sample_every"])
        self._length = streamer_args.get("length",60)
        self._streamer_args = streamer_args
        
    def start(self):
        self._streamer = source.create_web_streamer(**self._streamer_args)
        return StreamerWorker.start(self)
    
    def stream(self):
        count = 0
        t_end = time.time() + self._length
        streamer = self._streamer
        c_time = time.time()
        logging.info(f"Entering stream loop {c_time}")
        while  c_time < t_end:
            logging.info(f"Reading new frame")
            hasFrame, frame = streamer.read()
            logging.info(f"New frame read? {hasFrame} {count} {c_time}")
            if not hasFrame:
                break
            logging.info(f"New frame fetched {count} {c_time}")
            self._sink.sink(c_time,frame,count)
            count += 1
            time.sleep(self._sample_every)
            c_time = time.time()
        logging.info(f"Exiting stream loop {c_time}")
        self.done_callback()
    

    

