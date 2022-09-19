
from app.node.output import Output
import os
import logging
import json
from app.utils import rmtree,mkdir,rm_file, exists
from flask import current_app
import pandas as pd

class CSVWriter(Output):
    def __init__(self, name,prefix,
    xaxis = "",
    yaxis = "",
    overwrite=True):
        Output.__init__(self,name,prefix)
        self._filename = f"{prefix}/{name}.csv"
        self._xaxis = xaxis
        self._yaxis = yaxis
        self._df = None
        if exists(os.path.relpath(self._filename),self.context):
            rm_file(self._filename,self.context)
        
        logging.info(f"Creating folder {prefix}")
        mkdir(prefix,self.context)
        
        
    def write_meta(self,context):
        meta = {
            "type": "csv",
            "filename": f"{os.path.basename(self._filename)}",
            "x-axis": self._xaxis,
            "y-axis": self._yaxis
        }
        metafile = f"{self._prefix}/meta.json"
        logging.info(f"Creating meta data in {metafile}")
        with context.config["FS_OBJ"].open(
                os.path.relpath(metafile), "w"
            ) as f:
                f.write(json.dumps(meta))

    def run(self,context=None):
        """
        Safe node: input is assumed to be valid or can be handled properly
        """
        # expect dataframe object
        if context is None:
            context = self.context
        # TODO: refactor
        logging.info(f"Running {self.name} {self._filename}")
        try:
            self.write_meta(context)
            while self.more():
                item = self.get()
                logging.info(f"New item for {self.name}\n{item}")
                if self._df is None:
                    self._df = item
                else:
                    self._df = pd.concat([self._df,item])

                with context.config["FS_OBJ"].open(
                    os.path.relpath(self._filename), "w") as f:
                    logging.info(f"Writing to {os.path.relpath(self._filename)}")
                    f.write(self._df.to_csv(None,index=False))   
        except Exception as e:
            logging.erro(e)