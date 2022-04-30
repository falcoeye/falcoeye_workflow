
from app.node.node import Node
import os
class CSVWriter(Node):
    def __init__(self, name,filename):
        Node.__init__(self,name)
        self._filename = filename

    def run(self):
        # expect dataframe object
        while self.more():
            item = self.get()
            if os.path.exists(self._filename):
                item.to_csv(self._filename, mode='a', index=False, header=False)
            else:
                item.to_csv(self._filename, index=False)