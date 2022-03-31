import re
import subprocess as sp
from queue import Queue
from threading import Thread

import cv2
import numpy
import requests
import streamlink

from .sink import VideoFileSink


class Source:
    def __init__(self):
        pass

    def open(self):
        pass

    def read(self):
        pass

    def close(self):
        pass

class FileSource:
    def __init__(self, filename):
        self._filename = filename
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

    def read(self):
        return self._reader.read()

    def close(self):
        self._reader.release()
        self.width = -1
        self.height = -1
        self.frames_per_second = -1
        self.num_frames = -1

class StreamSource:
    resolutions = {"best": {"width": 1920, "height": 1080}}

    def __init__(self, url, queue_size=2000, resolution="best", sample_every=5, length=30):
        self.stopped = False
        self.url = url
        self.resolution = resolution
        self.sample_every = sample_every
        self.width = -1
        self.height = -1
        self.length = length
        self.frames_per_second = 30
        # initialize the queue used to store frames read from
        # the video stream
        self.Q = Queue(maxsize=queue_size)

    @staticmethod
    def create_stream_pipe(url, resolution):
        if url == None:
            return None

        try:
            streams = streamlink.streams(url)
        except streamlink.exceptions.NoPluginError:
            print(f"Warning: NO STREAM AVAILABLE in {url}")
            return None

        stream = streams[resolution]
        pipe = sp.Popen(
            [
                "/usr/local/bin/ffmpeg",
                "-i",
                stream.url,
                "-loglevel",
                "quiet",  # no text output
                "-an",  # disable audio
                "-f",
                "image2pipe",
                "-pix_fmt",
                "bgr24",
                "-vcodec",
                "rawvideo",
                "-",
            ],
            stdin=sp.PIPE,
            stdout=sp.PIPE,
        )
        return pipe

    def open(self):
        self.pipe = StreamSource.create_stream_pipe(self.url, self.resolution)
        if self.pipe:
            self.start_buffer()

    def close(self):
        self.stop()

    def start_buffer(self):
        # start a thread to read frames from the file video stream
        t = Thread(target=self.update_buffer, args=())
        t.daemon = True
        t.start()
        return self

    def update_buffer(self):

        count_frame = 0

        while count_frame < self.end:
            if count_frame % self.sample_every == 0:
                raw_image = self.pipe.stdout.read(
                    self.height * self.width * 3
                )  # read length*width*3 bytes (= 1 frame)

                frame = numpy.fromstring(raw_image, dtype="uint8").reshape(
                    (self.height, self.width, 3)
                )
                if not self.Q.full():
                    self.Q.put(frame)
                    count_frame += 1
                else:
                    count_frame += 1
                    continue
            else:
                count_frame += 1
                continue
        print("finished streaming")
        self.close()

    def read(self):
        # return next frame in the queue
        return True, self.Q.get()

    def more(self):
        # return True if there are still frames in the queue
        return self.Q.qsize() > 0

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        self.pipe.kill()

class AngelCamSource(StreamSource):
    resolution = {"best": {"width": 1920, "height": 1080}}

    def __init__(self, url, queue_size=2000, resolution="best", sample_every=5, end=30):
        StreamSource.__init__(self, url, queue_size, resolution, sample_every, end)
        self.m3u8 = None

    @staticmethod
    def capture_image(url, resolution="best"):
        c = requests.get(url).content.decode("utf-8")
        try:
            m3u8 = re.findall(r"\'https://.*angelcam.*token=.*\'", c)[0].strip("'")
        except IndexError:
            return None

        width = AngelCamSource.resolutions[resolution]["width"]
        height = AngelCamSource.resolutions[resolution]["height"]

        pipe = AngelCamSource.create_stream_pipe(m3u8, resolution)
        if not pipe:
            return False
        raw_image = pipe.stdout.read(height * width * 3)
        frame = numpy.fromstring(raw_image, dtype="uint8").reshape(
            (self.height, self.width, 3)
        )
        frame = frame[:, :, ::-1]
        pipe.kill()
        return frame

    def open(self):
        c = requests.get(self.url).content.decode("utf-8")
        self.m3u8 = re.findall(r"\'https://.*angelcam.*token=.*\'", c)[0].strip("'")
        checkIfStreamsWorks = self.create_pipe(self.m3u8)
        if checkIfStreamsWorks:
            self.start_buffer()

class YoutubeSource(StreamSource):
    resolutions = {
        "240p": {"width": 426, "height": 240},
        "360p": {"width": 640, "height": 360},
        "480p": {"width": 854, "height": 480},
        "720p": {"width": 1280, "height": 720},
        "1080p": {"width": 1920, "height": 1080},
    }

    def __init__(
        self, url, queue_size=2000, resolution="1080p", sample_every=5, length=30):
        StreamSource.__init__(self, url, queue_size, resolution, sample_every, length)
        self.width = YoutubeSource.resolutions[resolution]["width"]
        self.height = YoutubeSource.resolutions[resolution]["height"]
        self.pipe = None

    def open(self):
        # fetching is client responsiblity
        print(f"Creating pipe with {self.url}, {self.resolution}")
        self.pipe = YoutubeSource.create_stream_pipe(self.url, self.resolution)

    def read(self):
        raw_image = self.pipe.stdout.read(
                    self.height * self.width * 3
                )  # read length*width*3 bytes (= 1 frame)

        frame = numpy.fromstring(raw_image, dtype="uint8").reshape(
            (self.height, self.width, 3)
        )
        return True,frame
    
    @staticmethod
    def capture_image(url, resolution="1080p"):

        width = YoutubeSource.resolutions[resolution]["width"]
        height = YoutubeSource.resolutions[resolution]["height"]

        pipe = YoutubeSource.create_stream_pipe(url, resolution)
        if not pipe:
            return False

        raw_image = pipe.stdout.read(height * width * 3)
        frame = numpy.frombuffer(
            numpy.ascontiguousarray(raw_image), dtype="uint8"
        ).reshape((height, width, 3))
        # to rgb
        frame = frame[:, :, ::-1]
        pipe.kill()
        return frame

    @staticmethod
    def record_video(url, resolution="1080p", length=60, output_path=None):

        width = YoutubeSource.resolutions[resolution]["width"]
        height = YoutubeSource.resolutions[resolution]["height"]

        pipe = YoutubeSource.create_stream_pipe(url, resolution)
        if not pipe:
            return False

        # raw_image = pipe.stdout.read(height * width * 3)
        count_frame = 0
        lengthFrames = length * 30  # Assuming 30 frames per second
        sink = VideoFileSink(output_path)
        sink.open(30, width, height)
        while count_frame < lengthFrames:
            raw_image = pipe.stdout.read(
                height * width * 3
            )  # read length*width*3 bytes (= 1 frame)

            frame = numpy.fromstring(raw_image, dtype="uint8").reshape(
                (height, width, 3)
            )
            sink.sink(frame)
            count_frame += 1
        sink.close()
        pipe.kill()
        return True

def create_web_streamer(url, provider, resolution, sample_every, length):
    if provider == "angelcam":
        return AngelCamSource(
            url, resolution=resolution, sample_every=sample_every, length=length
        )
    elif provider == "youtube":
        return YoutubeSource(
            url, resolution=resolution, sample_every=sample_every, length=length
        )

def create_file_streamer(filepath, sample_every):
    return FileSource(filepath)

def capture_image(url, provider):
    if provider == "angelcam":
        return AngelCamSource.capture_image(url)
    elif provider == "youtube":
        return YoutubeSource.capture_image(url)

def record_video(url, provider, resolution, length, output_path):
    if provider == "youtube":
        return YoutubeSource.record_video(url, resolution, length, output_path)
