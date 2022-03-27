import json
import os
import threading

import requests
from app.io import source
from flask import current_app
from PIL import Image
import time
import sys

from app.utils import internal_err_resp, message

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

        
    def done_callback(self):
        self._done_callback(self._analysis_id)

    def stream(self):
        count = 0
        t_end = time.time() + self._length
        streamer = self._streamer
        c_time = time.time()
        while  c_time < t_end:
            hasFrame, frame = streamer.read()
            print("Frame fetched",flush=True)
            if not hasFrame:
                break
            self._sink.sink(c_time,frame,count)
            count += 1
            print("Streamer sleeping",self._sample_every)
            time.sleep(self._sample_every)
            print("Streamer awake")
            c_time = time.time()
        
        self.done_callback()
    

    

