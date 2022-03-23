import os

import cv2

from .sink import FileSink as FileSink


class VideoWriter:
    def __init__(self, filename):
        self._filename = filename

    def run(self, data):
        height, width = data[0].shape[:2]
        sink = FileSink(self._filename)
        sink.open(30, width, height)
        for f in data:
            f = cv2.cvtColor(f, cv2.COLOR_RGB2BGR)
            sink.sink(f)
        sink.close

    @classmethod
    def create(cls, **args):
        filename = args.get("output_path", None)
        if filename is None:
            print("csv outputer requires to pass output_path")
            exit(0)
        filedir = os.path.dirname(filename)
        if not os.path.exists(filedir):
            print(f"The parent directory for {filename} doesn't exist")
            exit(0)
        return VideoWriter(filename)


class MultiVideosWriter:
    def __init__(self, prefix):
        self._prefix = prefix

    def run(self, data):
        if len(data) == 0:
            print("Warning: no data to write")
            return
        if type(data[0]) != list:
            data = [data]

        height, width = data[0][0].shape[:2]
        for i, segment in enumerate(data):
            sink = FileSink(f"{self._prefix}_{i}.mp4")
            sink.open(30, width, height)
            for frame in segment:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                sink.sink(frame)
            sink.close

    @classmethod
    def create(cls, **args):
        prefix = args.get("output_prefix", None)
        if prefix is None:
            print("csv outputer requires to pass output_prefix")
            exit(0)
        filedir = os.path.dirname(prefix)
        if not os.path.exists(filedir):
            print(f"The parent directory for {prefix} doesn't exist")
            exit(0)
        return MultiVideosWriter(prefix)
