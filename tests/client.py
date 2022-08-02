

import requests
from PIL import Image
import numpy as np 
import json
import time


a = Image.open("../media/fish.jpg")
a = np.asarray(a)
from datetime import datetime
start=datetime.now()


data = json.dumps({"signature_name": "serving_default", "instances": [a.tolist()]})
headers = {"content-type": "application/json"}    
print("Posting now")
#response = requests.post("http://localhost:8501/v1/models/arabian_angelfish:predict",headers=headers,data=data)
response = requests.post("https://falcoeye-model-arabian-angelfish-xbjr6s7buq-uc.a.run.app/v1/models/arabian-angelfish:predict",headers=headers,data=data)

print(response.status_code)
# args = {
#         "email": "falcoeye-test@falcoeye.io",
#         "password": "falcoeye-test"
#     }

# pass_msgs =  [
#     "successfully logged in"
# ]
# backend_service = "https://falcoeye-backend-xbjr6s7buq-uc.a.run.app"
# res = requests.post(f"{backend_service}/auth/login", json=args)
# resdict = res.json()
# assert "access_token" in resdict
# header = {
#         "X-API-KEY": f'JWT {resdict["access_token"]}'
# }
# print(header)
# json_response = requests.get(f'{backend_service}/api/analysis/9d623771-7acc-46a4-848e-fee46ee3270d/meta.json', headers=header)
# print(json_response.status_code)
# print (datetime.now()-start)
