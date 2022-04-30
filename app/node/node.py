from queue import Queue
class Node:
    def __init__(self,name):
        self._name = name
        self._sinks = []
        self._data = Queue()
        self._thread = None
    
    def add_sink(self,sink):
        self._sinks.append(sink)
    
    def run(self):
        raise NotImplementedError
    
    def run_async(self):
        raise NotImplementedError
    
    def sink(self,data):
        for sink in self._sinks:
            sink._data.put(data)
    
    def more(self):
        return self._data.qsize() > 0
    
    def get(self):
        return self._data.get()