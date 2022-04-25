import cv2
from PIL import Image
import socket
from queue import Queue
import threading
from datetime import datetime
import asyncio
import aiohttp
import logging
import io
from PIL import Image
class Sink:
    def __init__(self):
        pass

    def open(self):
        pass

    def sink(self, frame):
        pass

    def close(self):
        pass

class VideoFileSink(Sink):
    def __init__(self, filename):
        Sink.__init__(self)
        self._filename = filename
        self._writer = None

    def open(self, frames_per_second, width, height):
        self._writer = cv2.VideoWriter(
            self._filename,
            fourcc=cv2.VideoWriter_fourcc(*"mp4v"),
            fps=float(frames_per_second),
            frameSize=(width, height),
            isColor=True,
        )

    def sink(self, frame):
        self._writer.write(frame)

    def close(self):
        self._writer.release()

class FalcoeyeAISink(Sink):
    def __init__(self,analysis_id,modelHandler,wf_handler):
        self._analysis_id = analysis_id
        self._modelHandler = modelHandler
        self._wf_handler = wf_handler
        self._queue = Queue()
        self._still = False
    
    def sink(self,c_time,frame,count):
        data = {
            "analysis_id": self._analysis_id,
            "count": count,
            "init_time": c_time
        }
        self._queue.put([frame,data])
        
    def more(self):
        return self._queue.qsize() > 0
        
    def close(self):
        self._still = False

    def start(self):
        self._still = True
        b_thread = threading.Thread(
                target=self.start_,
                args=(),
        )
        b_thread.daemon = True
        b_thread.start()
        return b_thread.is_alive()

    def start_concurrent(self):
        logging.info("Starting concurrent task")
        self._still = True
        self._loop = asyncio.new_event_loop()        
        
        b_thread = threading.Thread(
                target=self.start_background_loop,
                args=(self._loop,),
                daemon=True
        )
        b_thread.start()

        logging.info(f"Sinking thread started? {b_thread.is_alive()}")
        task = asyncio.run_coroutine_threadsafe(self.start_concurrent_(), self._loop)
        return b_thread.is_alive()
    
    def start_background_loop(self,loop: asyncio.AbstractEventLoop) -> None:
        asyncio.set_event_loop(loop)
        loop.run_forever()

    async def predict_async(self,session,frame,data):
        results_path =  await self._modelHandler.predict_async(session,frame,data)
        logging.info("Results received")
        
    async def start_concurrent_(self):
        tasks = []
        logging.info("Entering sinking loop")
        async with aiohttp.ClientSession() as session:
            while self._still or self.more():
                if self.more():
                    logging.info("New data to sink")
                    frame,data = self._queue.get()
                    task = asyncio.create_task(self.predict_async(session,frame,data))
                    tasks.append(task)
            logging.info("Exiting sinking loop")
            await asyncio.gather(*tasks)
        self._wf_handler.done_sinking()
        self._loop.stop()
  
    def start_(self):
        while self._still or self.more():
            if self.more():
                logging.info("New data to sink")
                frame,data = self._queue.get()
                results_path =  self._modelHandler.predict(frame,data)
                logging.info("Results received")
                self._wf_handler.put(results_path)
        self._wf_handler.done_sinking()

class TFServingSink(FalcoeyeAISink):
    def __init__(self,analysis_id,modelHandler,wf_handler):
        FalcoeyeAISink.__init__(self,analysis_id,modelHandler,wf_handler)

    async def predict_async(self,session,frame,data):
        logging.info(data)
        logging.info("Packaging data")
        try:
          response =  await self._modelHandler.predict_async(session,frame,data)
          logging.info(response)
          self._wf_handler.put((frame,response))
        except Exception as e:
            logging.error(e)

    def start_(self):
        while self._still or self.more():
            if self.more():
                logging.info("New data to sink")
                frame,data = self._queue.get()
                response =  self._modelHandler.predict(frame,data)
                logging.info("Results received")
                self._wf_handler.put((frame,response))
        self._wf_handler.done_sinking()

class ImageSink(Sink):
    def __init__(self, filename):
        Sink.__init__(self)
        self._filename = filename

    def open(self):
        pass

    def sink(self, frame):
        Image.fromarray(frame).save(self._filename)

    def close(self):
        pass

