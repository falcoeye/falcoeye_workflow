from app.node.node import Node
from threading import Thread
import logging
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
        
        logging.info(f"Sequence {self.name} inturrepted. Flushing queue")
        if self._done_callback:
            self._done_callback(self._name)  
        self.close_sinks() 

    def run_async(self,done_callback):
        self._done_callback = done_callback
        self._continue = True
        self._thread = Thread(target=self.run_forever_, args=(),daemon=True)
        self._thread.start()

