from .core import FalcoServingKube
from .tf import start_tfserving
from .torch import start_torchserving
import logging
CALLED_SERVER = {}

def start_service(model_name,vendor,model_version,protocol):
	if vendor == "tf":
		return start_tfserving(model_name,model_version,protocol)
	elif vendor == "torch":
		return start_torchserving(model_name,model_version,protocol)

def get_service_server(model_name,vendor,
	model_version,protocol,run_if_down):
	logging.info("getting service address")
	
	if model_name in CALLED_SERVER and CALLED_SERVER[model_name] and CALLED_SERVER[model_name].is_running():
		return CALLED_SERVER[model_name]
	elif run_if_down:
	   logging.info(f"Starting container for {model_name}") 
	   server = start_service(model_name,vendor,model_version,protocol)
	   CALLED_SERVER[model_name] = server
	   return server
	else:
		logging.error(f"Couldn't find running container for {model_name}")
		return None



