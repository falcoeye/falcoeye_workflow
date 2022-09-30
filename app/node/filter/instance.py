
from app.node.node import Node
import logging
class TypeFilter(Node):
    def __init__(self, name, keys):
        Node.__init__(self,name)
        self._keys = keys

    def run(self,context=None):
        # expecting items of type FalcoeyeDetction
        while self.more():
            item = self.get()
            # TODO: maybe optimize in one loop 
            classes = item.get_classes()
            for i,c in enumerate(classes):
                if c not in self._keys:
                    item.delete(i)

class SizeFilter(Node):
    def __init__(self, name, width_threshold,height_threshold):
        Node.__init__(self,name)
        self._width_threshold = width_threshold
        self._height_threshold = height_threshold

    def run(self,context=None):
        # expecting items of type FalcoeyeDetction
        logging.info(f"Running {self.name} with {self._width_threshold} and {self._height_threshold}")
        while self.more():
            item = self.get()   
            for i in range(item.count):
                if item.iwidth(i) > self._width_threshold or item.iheight(i) > self._height_threshold:
                    item.delete(i)