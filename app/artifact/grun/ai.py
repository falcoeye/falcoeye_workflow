import json
import requests
from flask import current_app
import logging
from google.cloud.run_v2.services.services.client import ServicesClient
import numpy as np
import tensorflow as tf
from tensorflow_serving.apis import predict_pb2


client = ServicesClient()
SERVERS = {}

def get_service_server(model_name,model_version,protocol,run_if_down):
	if model_name in SERVERS:
		return SERVERS[model_name]
	logging.info(f"Requesting {model_name} info with protocol {protocol}")
	if protocol.lower() == "restful":
		sn = f"projects/{current_app.config['FS_PROJECT_ID']}/locations/{current_app.config['FS_LOCATION']}/services/falcoeye-model-{model_name}"
		resp = client.get_service(name=sn)
		if "uri" in resp:
			service_address = resp.uri
			logging.info(f"Service uri for {model_name}: {service_address}")
			SERVERS[model_name] = TensorflowServingRESTful(model_name,model_version,service_address)
		else:
			return None
	
	elif protocol.lower() == "grpc":    
		sn = f"projects/{current_app.config['FS_PROJECT_ID']}/locations/{current_app.config['FS_LOCATION']}/services/falcoeye-model-{model_name}-grpc"
		resp = client.get_service(name=sn)
		logging.info(f"gRPC service name {sn}")
		if "uri" in resp:
			service_address = resp.uri
			service_address = service_address.replace("https://","")
			service_address = f'{service_address}:443'
			logging.info(f"Service uri for {model_name}: {service_address}")
			SERVERS[model_name] = TensorflowServinggRPC(model_name,model_version,service_address)
		else:
			return None
		
	
	return SERVERS[model_name]

class TensorflowServing:
	def __init__(self,
		model_name,
		model_version,
		service_address):
		self._name = model_name
		self._version = model_version
		self._service_address = service_address
		
	@property
	def service_address(self):
		return self._service_address

	def post(self):
		raise NotImplementedError
	
	async def post_async(self,session,frame):
		raise NotImplementedError

class TensorflowServingRESTful(TensorflowServing):
	def __init__(self,
		model_name,
		model_version,
		service_address):
		TensorflowServing.__init__(self,model_name,
			model_version,service_address)
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

class TensorflowServinggRPC(TensorflowServing):
	def __init__(self,
		model_name,
		model_version,
		service_address):

		TensorflowServing.__init__(self,model_name,model_version,service_address)
		logging.info(f"New gRPC tensorflow serving initialized for {model_name} on {service_address}")

	def post(self,frame):
		raise NotImplementedError

	async def post_async(self,stub,frame):
		try:
			request = predict_pb2.PredictRequest()
			request.model_spec.name = self._name
			request.model_spec.signature_name = 'serving_default'
			frame = np.expand_dims(frame, axis=0) 
			request.inputs['input_tensor'].CopyFrom(tf.make_tensor_proto(frame))

			logging.info(f"Posting new frame asynchronously to gRPC")
			result = await stub.Predict(request)
			logging.info("Prediction received")
			# To match resful response
			boxes = np.array(result.outputs['detection_boxes'].float_val).reshape((-1,4)).tolist()
			classes = result.outputs['detection_classes'].float_val
			scores = result.outputs['detection_scores'].float_val
			detections = {'detection_boxes': boxes,
				'detection_classes':classes,
				'detection_scores': scores}
			return detections
		except Exception as e:
			raise
			logging.error(e)