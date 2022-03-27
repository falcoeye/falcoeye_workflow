import json
from PIL import Image
from base64 import decodestring
import numpy as np
import os

class DataFetcher:
    def __init__(self):
        pass
    def fetch(self):
        pass

class LocalStorageDataFetcher(DataFetcher):
    def __init__(self):
        DataFetcher.__init__(self)
        self._replace = {"/predictions/": "/Users/jalalirs/Documents/code/falcoeye/falcoeye_ai/predictions/"}
    
    def fetch(self,path):
        for rf, rt in self._replace.items():
            path = path.replace(rf,rt)
        
        with open(f'{path}/prediction.json') as f:
            prediction = json.load(f)
        
        frame = Image.open(f'{path}/frame.png')
        framearr = np.asarray(frame).copy()
        frame.close()
        
        return framearr,prediction
       