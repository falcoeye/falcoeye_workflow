from .core import FalcoServingKube
from .tf import start_tfserving
from .torch import start_torchserving
import logging
from threading import Lock

# TODO: really?!!!
SERVICES = {}
START_PORT = 5800
lock = Lock()

def start_service(model_name,vendor,model_version,port,protocol):
	if vendor == "tf":
		return start_tfserving(model_name,model_version,port,protocol)
	elif vendor == "torch":
		return start_torchserving(model_name,model_version,port,protocol)

def get_service_server(model_name,vendor,
	model_version,protocol,run_if_down):
	logging.info("getting service address")
	
	if model_name in SERVICES and SERVICES[model_name] and SERVICES[model_name].is_running():
		return SERVICES[model_name]
	elif run_if_down:
		logging.info(f"Starting container for {model_name}")
		with lock:
			port = START_PORT
			while FalcoServingKube.is_port_taken(port):
				port += 1

		server = start_service(model_name,vendor,model_version,port,protocol)
		SERVICES[model_name] = server
		return server
	else:
		logging.error(f"Couldn't find running container for {model_name}")
		return None



