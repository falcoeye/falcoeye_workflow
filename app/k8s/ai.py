import json
import requests
from falcoeye_kubernetes import FalcoServingKube
from flask import current_app

def start_tfserving_container(model_name, model_version):
    kube = FalcoServingKube(model_name)
    if kube.start():
        return TensorflowServingContainer(model_name,model_version,kube)
    else:
        return None

class TensorflowServingContainer:
    def __init__(self,
        model_name,
        model_version,
        kube):
        self._name = model_name
        self._version = model_version
        self._running = True
        self._kube = kube
        if current_app.config.get("TESTING"):
            self._server_address = self._kube.get_service_address(external=True,hostname=True)
        else:
            self._server_address = self._kube.get_service_address()
        
        self._predict_url = f"http://{self._server_address}/v{model_version}/models/{model_name}:predict"
      
    def is_running(self):
        return self._running

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
            async with session.post(self._predict_url,data=data,headers=headers) as response:
                logging.info("waiting for response")
                responseText = await response.text()
                predictions = json.loads(responseText)['predictions'][0]
                return predictions
        except Exception as e:
            logging.error(e)