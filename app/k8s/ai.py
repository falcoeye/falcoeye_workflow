import json
import requests
from app.k8s.utils import get_ip_address


def start_tfserving_container(model_name,model_version):
    # TODO: start container if not started
    ip = "localhost"#get_ip_address(model_name)
    port = 8501
    server = f"http://{ip}:{port}/v{model_version}/models/{model_name}:predict"

    return TensorflowServingContainer(model_name,model_version,server)

class TensorflowServingContainer:
    def __init__(self,
        model_name,
        model_version,
        server):
        self._name = model_name
        self._version = model_version
        self._running = True
        self._server = server
      
    def is_running(self):
        return self._running

    def post(self,frame):
        data = json.dumps({"signature_name": "serving_default", "instances": [frame.tolist()]})
        headers = {"content-type": "application/json"}
        response = requests.post(self._server, data=data, headers=headers)
        predictions = json.loads(response.text)['predictions'][0]
        return predictions

    async def post_async(self,session,frame):
        try:
            data = json.dumps({"signature_name": "serving_default", "instances": [frame.tolist()]})
            headers = {"content-type": "application/json"}
            async with session.post(self._server,data=data,headers=headers) as response:
                logging.info("waiting for response")
                responseText = await response.text()
                predictions = json.loads(responseText)['predictions'][0]
                return predictions
        except Exception as e:
            logging.error(e)