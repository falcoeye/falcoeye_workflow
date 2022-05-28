
from app.node.output import Output
import os
import logging
import json

class CSVWriter(Output):
    def __init__(self, name,prefix,
    xaxis = "",
    yaxis = "",
    overwrite=True):
        Output.__init__(self,name,prefix)
        self._filename = f"{prefix}/{name}.csv"
        self._xaxis = xaxis
        self._yaxis = yaxis
        if os.path.exists(self._filename):
            os.remove(self._filename) 
        
    def write_meta(self):
        meta = {
            "type": "csv",
            "filename": f"{self._filename}",
            "x-axis": self._xaxis,
            "y-axis": self._yaxis
        }
        with open(f'{self._prefix}/meta.json',"w") as f:
            f.write(json.dumps(meta))

    def run(self):
        # expect dataframe object
        logging.info(f"Running {self.name}")
        os.makedirs(os.path.dirname(self._filename),exist_ok=True)
        self.write_meta()
        while self.more():
            item = self.get()
            logging.info(f"New item for {self.name}\n{item}")
            if os.path.exists(self._filename):
                item.to_csv(self._filename, mode='a', index=False, header=False)
            else:
                item.to_csv(self._filename, index=False)