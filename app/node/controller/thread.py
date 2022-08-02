from app.node.node import Node
from threading import Thread
import logging
import aiohttp
import asyncio
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


class ConcurrentPostTasksThreadWrapper(Node):
    
    def __init__(self,name,node,tcplimit=2):
        Node.__init__(self,name)
        self._node = node
        self._loop = None
        self._tcplimit = tcplimit
        self._ntasks = tcplimit

    async def task_(self,session,item):
        logging.info(f"Running task asyncronously for frame {item.framestamp}")
        o = await self._node.run_on_async(session,item)
        self.sink(o)

    async def run_forever_(self):
        logging.info(f"Starting concurrent looping for {self.name}")        
        tasks = []
        connector = aiohttp.TCPConnector(limit=self._tcplimit)
        async with aiohttp.ClientSession(connector=connector) as session:
            logging.info(f"async session defined with {self._tcplimit} tcp limits for {self.name}")        
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
        self._loop.stop()
        
        logging.info(f"Loop {self.name} inturrepted. Flushing queue")
        if self._done_callback:
            self._done_callback(self._name)  
        self.close_sinks() 

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