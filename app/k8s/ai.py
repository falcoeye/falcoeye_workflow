import json
import requests
from falcoeye_kubernetes import FalcoServingKube
from flask import current_app
import logging

def get_service_address(kube):
    logging.info("getting service address")
    if current_app.config.get("TESTING"):
        return kube.get_service_address(external=True,hostname=True)
    else:
        return kube.get_service_address()

def start_tfserving_container(model_name, model_version):
    kube = FalcoServingKube(model_name)
    started = kube.start() and kube.is_running()
    logging.info(f"kube started for {model_name}?: {started}")
    if started:
        service_address = get_service_address(kube)
        logging.info(f"New container for {model_name} started")
        return TensorflowServingContainer(model_name,model_version,service_address,kube)
    else:
        logging.error(f"Couldn't start container for {model_name}")
        return None

class TensorflowServingContainer:
    def __init__(self,
        model_name,
        model_version,
        service_address,
        kube):
        self._name = model_name
        self._version = model_version
        self._kube = kube
        self._predict_url = f"http://{service_address}/v{model_version}/models/{model_name}:predict"
        logging.info(f"New tensorflow serving container initialized for {model_name} on {service_address}")

    def post(self,frame):
        # TODO: what if kube is not running?
        data = json.dumps({"signature_name": "serving_default", "instances": [frame.tolist()]})
        headers = {"content-type": "application/json"}
        response = requests.post(self._predict_url, data=data, headers=headers)
        predictions = json.loads(response.text)['predictions'][0]
        return predictions

    async def post_async(self,session,frame):
        try:
            # TODO: what if kube is not running?     
            data = json.dumps({"signature_name": "serving_default", "instances": [frame.tolist()]})
            headers = {"content-type": "application/json"}
            logging.info(f"Posting new frame asynchronously {self._predict_url}")
            async with session.post(self._predict_url,data=data,headers=headers) as response:
                logging.info("Prediction received")
                responseText = await response.text()
                predictions = json.loads(responseText)['predictions'][0]
                return predictions
        except Exception as e:
            raise
            logging.error(e)