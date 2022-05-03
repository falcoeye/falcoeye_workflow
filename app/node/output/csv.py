
from app.node.node import Node
import os
import logging
class CSVWriter(Node):
    def __init__(self, name,filename,overwrite=True):
        Node.__init__(self,name)
        self._filename = filename
        if os.path.exists(self._filename):
            os.remove(self._filename) 

    def run(self):
        # expect dataframe object
        logging.info(f"Running {self.name}")
        os.makedirs(os.path.dirname(self._filename),exist_ok=True)
        while self.more():
            item = self.get()
            logging.info(f"New item for {self.name}\n{item}")
            if os.path.exists(self._filename):
                item.to_csv(self._filename, mode='a', index=False, header=False)
            else:
                item.to_csv(self._filename, index=False)