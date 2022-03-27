import json
import os
import threading

import requests
from falcoeye_core.io import source
from flask import current_app
from PIL import Image

from app.utils import internal_err_resp, message

class Sink:
    url = "http://localhost:9000"
    def __init__(self,analysis_id):
        self._analysis_id = analysis_id

    def sink(frame,count):
        data = {
            "analysis_id": self._analysis_id,
            "frame": frame,
            "count": count
        }
        rv = requests.post(f"{Sink.url}/predict", data=json.dumps(data))


class WebStreamWorker:
    def __init__(self,analysis_id,url,stream_provider,resolution,length,sink):
        self._analysis_id = analysis_id
        self._url = url
        self._stream_provider = stream_provider
        self._resolution = resolution
        self._length = length
        self._sink = sink
        self._streamer = None
        self._done_callback = None


    def start(self,callback):
        self._done_callback = callback

        b_thread = threading.Thread(
                target=Streamer.stream,
                args=(self),
            )
        b_thread.start()

    def done_callback(self)
        self._done_callback(self._analysis_id)

    @staticmethod
    def stream(handler):
        streamer = source.create_streamer(url, stream_provider,resolution,length,output_path)
        nFrames = handler._length
        count = 0
        while count < nFrames:
            hasFrame, frame = streamer.read()
            if not hasFrame:
                break
            handler._sink.sink(frame,count)
            count += 1
        
        handler.done_callback()
    

    

