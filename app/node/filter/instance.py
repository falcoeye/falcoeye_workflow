
from app.node.node import Node

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