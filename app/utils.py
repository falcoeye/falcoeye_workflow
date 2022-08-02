import os
import base64
import string
import random
from flask import current_app
import logging
from datetime import datetime
from google.cloud import storage
import shutil
TYPE_MAP = {"int": int, "str": str, "float": float, "list": list}


def check_type(variable, str_type):
	return type(variable) == TYPE_MAP[str_type]


def try_cast(variable, str_type):
	try:
		variable = TYPE_MAP[str_type](variable)
		return variable
	except:
		return False

def array_to_base64(arr):
	return base64.b64encode(arr)


def message(status, message):
	response_object = {"status": status, "message": message}
	return response_object


def validation_error(status, errors):
	response_object = {"status": status, "errors": errors}

	return response_object


def err_resp(msg, reason, code):
	err = message(False, msg)
	err["error_reason"] = reason
	return err, code


def internal_err_resp():
	err = message(False, "Something went wrong during the process!")
	err["error_reason"] = "server_error"
	return err, 500

def mkdir(path,app=None):
	# To avoid Working outside of application context error
	try:
		logging.info(f"mkdir is called with {path} {app}")
		path = os.path.relpath(path)
		if app is None:
			app = current_app
		
		FS_OBJ = app.config["FS_OBJ"]
		if FS_OBJ.isdir(path):
			return
		if app.config["FS_IS_REMOTE"]:
			if not path.endswith("/"):
				path = path + "/"
			FS_OBJ.touch(path)
		else:
			FS_OBJ.makedirs(path)
	except Exception as e:
		logging.error(e)

def put(f_from, f_to,app=None):
	if app is None:
		app = current_app

	FS_OBJ = app.config["FS_OBJ"]
	
	if app.config["FS_IS_REMOTE"]:
		logging.info(f"Remote put: copying from {f_from} to {f_to}")
		FS_OBJ.put(f_from, f_to)
	else:
		logging.info(f"Local put: copying from {f_from} to {f_to}")
		shutil.copy2(f_from, f_to)

def rmtree(path,app=None):
	if app is None:
		app = current_app

	FS_OBJ = app.config["FS_OBJ"]

	path = os.path.relpath(path)
	if not path.endswith("/"):
		path = path + "/"

	if not FS_OBJ.isdir(path):
		return
	if app.config["FS_IS_REMOTE"]:
		FS_OBJ.delete(path, recursive=True)
	else:
		shutil.rmtree(path)

def random_string(N=6):
	randomstr = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
	logging.info(f"random_string called with N={N}: returning {randomstr}")
	return randomstr

def tempdir():
	import platform
	import tempfile
	tempdir = "/tmp" if platform.system() == "Darwin" else tempfile.gettempdir()
	logging.info(f"tempdir called: return {tempdir}")
	return tempdir

def download_file(filename, context=None):
	if context is None:
		context = current_app

	if not context.config["FS_IS_REMOTE"]:
		return filename

	logging.info(f"Downloading {filename}")
	filename = filename.replace("//", "/") 
	parts = filename.split("/")
	blob_name = "/".join(parts[1:])
	bucket_name = parts[0]
	tempfile =  f'{tempdir()}/{datetime.now().strftime("%m_%d_%Y")}_{random_string()}.mp4'
	logging.info(f"Downloading blob {blob_name} from {bucket_name} bucket into {tempfile}")
	bucket = storage.Client().bucket(bucket_name)
	blob = bucket.blob(blob_name)
	blob.download_to_filename(tempfile)

	return tempfile

def exists(path, context=None):
	if context is None:
		context = current_app

	if context.config["FS_IS_REMOTE"] :
		return context.config["FS_OBJ"].exists(path)
	else:
		return os.path.exists(path)

def rm_file(filename, context=None):
	if context is None:
		context = current_app

	logging.info(f"Removing {filename}")	
	# TODO: this function is being called by different purposes 
	# must be refactored
	if filename.startswith("/tmp/"):
		os.remove(filename)
	elif context.config["FS_IS_REMOTE"] :
		context.config["FS_OBJ"].delete(filename)
	else:
		os.remove(filename)
		
	
	