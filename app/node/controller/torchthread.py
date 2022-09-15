from .thread import ConcurrentRequestTaskThreadWrapper
import asyncio
from grpc import aio
import grpc
import logging
import aiohttp
from app.artifact.k8s.torch import InferenceAPIsServiceStub
from flask import current_app

class ConcurrentTorchgRPCTasksThreadWrapper(ConcurrentRequestTaskThreadWrapper):
    GRPC_MAX_RECEIVE_MESSAGE_LENGTH = 4096*4096*3
    def __init__(self,name,node,ntasks=2):
        ConcurrentRequestTaskThreadWrapper.__init__(self,name,node,ntasks)
        self._options  = [
                    ('grpc.max_send_message_length', ConcurrentTorchgRPCTasksThreadWrapper.GRPC_MAX_RECEIVE_MESSAGE_LENGTH),
                    ('grpc.max_receive_message_length', ConcurrentTorchgRPCTasksThreadWrapper.GRPC_MAX_RECEIVE_MESSAGE_LENGTH)]

        
    async def run_forever_(self,context=None):
        if context is None:
            context = current_app

        try:
            host = self._node.get_service_address() 
            logging.info(f"Starting concurrent gRPC looping for {self.name} on {host}")  
            if context.config["FS_IS_REMOTE"]:
                async with aio.secure_channel(host,
                    grpc.ssl_channel_credentials(),options=self._options) as channel:
                    stub = InferenceAPIsServiceStub(channel)
                    logging.info(f"Starting stub looping for {self.name} with {self._ntasks} tasks in secure_channel") 
                    await self.run_session_loop_(stub)
            else:
                async with aio.insecure_channel(host, options=self._options) as channel:
                    stub = InferenceAPIsServiceStub(channel)
                    logging.info(f"Starting stub looping for {self.name} with {self._ntasks} tasks in insecure_channel") 
                    await self.run_session_loop_(stub)
            self._loop.stop()
            
            logging.info(f"Loop {self.name} inturrepted. Flushing queue")
            if self._done_callback:
                self._done_callback(self._name)  
            self.close_sinks() 
        except Exception as e:
            logging.error(e)
