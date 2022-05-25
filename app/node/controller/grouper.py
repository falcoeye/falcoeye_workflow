from app.node.node import Node
from threading import Thread
import logging
class SequenceRunner(Node):
    
    def __init__(self,name,nodes,frequency=1):
        Node.__init__(self,name)
        self._nodes = nodes
        self._frequency = frequency
        self._counter = 0
        self._sinks = [self._nodes[0]]
    
    def run_(self):
        self._counter += 1
        logging.info(f"Buffering sequence {self._counter}/{self._frequency}")
        if self._counter == self._frequency: 
            logging.info(f"Runing sequence now")
            for n in self._nodes:
                logging.info(f"Runing node {n.name}")
                n.run()  
            self._counter = 0

    def run(self):
        self.open_nodes()
        while self.more():
            item = self.get()
            self.sink(item)
            self.run_()
        if self._counter != 0:
            # tricking the run_ function to force it to run
            self._counter = self._frequency - 1
            self.run_()
        self.close_nodes()
        # run last time to flush. Some nodes have post close scenarios
        logging.info("Flushing nodes after closing.")
        for n in self._nodes:
            logging.info(f"Runing node {n.name}")
            n.run()  
            
    def run_forever_(self):
        # opening the nodes (i.e. setting continue to True)
        self.open_nodes()
        logging.info(f"Starting looping for {self.name}")
        while self._continue or self.more():
            if not self.more():
                continue

            logging.info(f"New item for {self.name} sequence")
            item = self.get()
            self.sink(item)
            self.run_()
        logging.info(f"Sequence {self.name} inturrepted.")
        # flushing the remaining
        if self._counter != 0:
            logging.info(f"Flushing queue for {self.name}. {self._counter} item not processed")
            # tricking the run_ function to force it to run
            self._counter = self._frequency - 1
            self.run_()
        logging.info(f"Sequence {self.name} loop exited")
        self._counter = 0
        if self._done_callback:
            self._done_callback(self._name)
        
        # closing the nodes (i.e. setting continue to False)
        self.close_nodes()
        # TODO: refactor this
        # run last time to flush. Some nodes have post close scenarios
        logging.info("Flushing nodes after closing.")
        for n in self._nodes:
            logging.info(f"Runing node {n.name}")
            n.run()  
    
    def open_nodes(self):
        for node in self._nodes:
            node.open() 

    def close_nodes(self):
        for node in self._nodes:
            node.close() 

    def run_async(self,done_callback,error_callback):
        self._done_callback = done_callback
        self._continue = True
        self._thread = Thread(target=self.run_forever_, args=(),daemon=True)
        self._thread.start()