import json
import requests
from flask import current_app
import logging
from google.cloud.run_v2.services.services.client import ServicesClient

client = ServicesClient()
SERVERS = {}

def get_service_server(model_name,model_version,run_if_down):
    if model_name in SERVERS:
        return SERVERS[model_name]
    logging.info("Requesting findfish info")
    sn = f"projects/{current_app.config['FS_PROJECT_ID']}/locations/{current_app.config['FS_LOCATION']}/services/falcoeye-model-{model_name}"
    resp = client.get_service(name=sn)
    if "uri" in resp:
        service_address = resp.uri
        logging.info(f"Service uri for {model_name}: {service_address}")
        SERVERS[model_name] = TensorflowServing(model_name,model_version,service_address)
        return SERVERS[model_name]
    else:
        return None
    

class TensorflowServing:
    def __init__(self,
        model_name,
        model_version,
        service_address):
        self._name = model_name
        self._version = model_version
        self._predict_url = f"{service_address}/v{model_version}/models/{model_name}:predict"
        logging.info(f"New tensorflow serving initialized for {model_name} on {service_address}")

    def post(self,frame):
        data = json.dumps({"signature_name": "serving_default", "instances": [frame.tolist()]})
        headers = {"content-type": "application/json"}
        response = requests.post(self._predict_url, data=data, headers=headers)
        predictions = json.loads(response.text)['predictions'][0]
        return predictions

    async def post_async(self,session,frame):
        try:
            data = json.dumps({"signature_name": "serving_default", "instances": [frame.tolist()]})
            headers = {"content-type": "application/json"}
            logging.info(f"Posting new frame asynchronously {self._predict_url}")
            async with session.post(self._predict_url,data=data,headers=headers) as response:
                logging.info("Prediction received")
                responseText = await response.text()
                predictions = json.loads(responseText)['predictions'][0]
                return predictions
        except Exception as e:
            logging.error(e)
            return None