
from app.node.node import Node


class Source(Node):
    def __init__(self,name,**kwargs):
        Node.__init__(self,name)

    def open(self):
        pass

    def read(self):
        pass

    def close(self):
        pass


