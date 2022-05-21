

import requests
from PIL import Image
import numpy as np 
import json
import time


a = Image.open("./tests/media/fish.jpg")
a = np.asarray(a)
from datetime import datetime
start=datetime.now()


data = json.dumps({"signature_name": "serving_default", "instances": [a.tolist()]})
headers = {"content-type": "application/json"}      
json_response = requests.post('http://localhost:8501/v1/models/arabianangelfish:predict', data=data, headers=headers)

print (datetime.now()-start)