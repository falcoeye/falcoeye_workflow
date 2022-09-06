from app.node.node import Node
from threading import Thread
import logging
import aiohttp
from flask import current_app
import asyncio
from grpc import aio
import grpc
from tensorflow_serving.apis import prediction_service_pb2_grpc

class ThreadWrapper(Node):
    def __init__(self,name,node):
        Node.__init__(self,name)
        self._node = node

    def run_forever_(self):
        logging.info(f"Starting looping for {self.name}")
        while self._continue or self.more():
            if not self.more():
                continue
            logging.info(f"New item for {self.name} sequence")
            item = self.get()
            node_res = self._node.run_on(item)
            self.sink(node_res)
        
        logging.info(f"Loop {self.name} inturrepted. Flushing queue")
        if self._done_callback:
            self._done_callback(self._name)  
        self.close_sinks() 

    def run_async(self,done_callback,error_callback):
        self._done_callback = done_callback
        self._continue = True
        self._thread = Thread(target=self.run_forever_, args=(),daemon=True)
        self._thread.start()

class ConcurrentRequestTaskThreadWrapper(Node):
    def __init__(self,name,node,ntasks=2):
        Node.__init__(self,name)
        self._node = node
        self._loop = None
        self._ntasks = ntasks
    
    async def task_(self,session,item):
        logging.info(f"Running task asyncronously for frame {item.framestamp}")
        o = await self._node.run_on_async(session,item)
        self.sink(o)
    
    def start_background_loop(self,loop: asyncio.AbstractEventLoop) -> None:
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def run_async(self,done_callback,error_callback):
        self._done_callback = done_callback
        self._error_callback = error_callback
        self._continue = True
        self._loop = asyncio.new_event_loop()     
        self._thread = Thread(target=self.start_background_loop,
                args=(self._loop,),
                daemon=True)
        self._thread.start()
        asyncio.run_coroutine_threadsafe(self.run_forever_(), self._loop)
 
    def run_forever_(self):
        raise NotImplementedError

    async def run_session_loop_(self,session):
        try:
            tasks = []
            while self._continue or self.more():
                if self.more():
                    logging.info("New data to sink")
                    item = self.get()
                    logging.info(f"Creating task for frame {item.framestamp} with size {item.size}")
                    task = asyncio.create_task(self.task_(session,item))
                    tasks.append(task)
                    logging.info(f"Task created for frame {item.framestamp}")
                if len(tasks) == self._ntasks:
                    logging.info(f"Gathering {self._ntasks} new tasks")
                    await asyncio.gather(*tasks)
                    tasks = []
            if len(tasks) > 0:
                logging.info("Gathering remaining tasks")
                await asyncio.gather(*tasks)
                tasks = []
            logging.info("Exiting sinking loop")
        except Exception as e:
            logging.error(e)

class ConcurrentPostTasksThreadWrapper(ConcurrentRequestTaskThreadWrapper):
    
    def __init__(self,name,node,ntasks=2):
        ConcurrentRequestTaskThreadWrapper.__init__(self,name,node,ntasks)
        self._tcplimit = ntasks

    async def run_forever_(self):
        logging.info(f"Starting concurrent looping for {self.name}")        
        
        connector = aiohttp.TCPConnector(limit=self._tcplimit)
        async with aiohttp.ClientSession(connector=connector) as session:
            logging.info(f"Starting aiohttp looping for {self.name} with {self._ntasks} tasks") 
            await self.run_session_loop_(session)

        self._loop.stop()
        logging.info(f"Loop {self.name} inturrepted. Flushing queue")
        if self._done_callback:
            self._done_callback(self._name)
        self.close_sinks() 

class ConcurrentgRPCTasksThreadWrapper(ConcurrentRequestTaskThreadWrapper):
    GRPC_MAX_RECEIVE_MESSAGE_LENGTH = 4096*4096*3
    def __init__(self,name,node,ntasks=2,max_send_message_length=6220800):
        ConcurrentRequestTaskThreadWrapper.__init__(self,name,node,ntasks)
        self._max_send_message_length = max_send_message_length
        self._options  = [
                    ('grpc.max_send_message_length', ConcurrentgRPCTasksThreadWrapper.GRPC_MAX_RECEIVE_MESSAGE_LENGTH),
                    ('grpc.max_receive_message_length', ConcurrentgRPCTasksThreadWrapper.GRPC_MAX_RECEIVE_MESSAGE_LENGTH)]
    async def run_forever_(self,context=None):
        if context is None:
            context = current_app

        try:
            host = self._node.get_service_address()
            
            logging.info(f"Starting concurrent gRPC looping for {self.name} on {host}")  
            if context.config["FS_IS_REMOTE"]:
                async with aio.secure_channel(host, 
                    grpc.ssl_channel_credentials(), options=self._options) as channel:
                    stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
                    logging.info(f"Starting stub looping for {self.name} with {self._ntasks} tasks in secure_channel") 
                    await self.run_session_loop_(stub)
            else:
                async with aio.insecure_channel(host, options=self._options) as channel:
                    stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
                    logging.info(f"Starting stub looping for {self.name} with {self._ntasks} tasks in insecure_channel") 
                    await self.run_session_loop_(stub)
            self._loop.stop()
            
            logging.info(f"Loop {self.name} inturrepted. Flushing queue")
            if self._done_callback:
                self._done_callback(self._name)  
            self.close_sinks() 
        except Exception as e:
            logging.error(e)
