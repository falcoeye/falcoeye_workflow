from flask import current_app

from app.utils import err_resp, internal_err_resp, message,random_string
from app.k8s.core import FalcoJobKube
import json
import logging

class AnalysisService:
	# Used for testing purposes only
	ANALYSIS = {}
	@staticmethod
	def new_analysis(data):
		logging.info(f"New analysis requested")
		analysis_file = data["analysis_file"]
		
		with open(analysis_file) as f:
			data = json.load(f)
		
		analysis = data["analysis"]
		inline = data["workflow"].get("inline",False)

		kube = FalcoJobKube(analysis['id'],analysis_file)
		job = kube.start() 
		logging.info(f"Job kube started for {analysis['id']}")
		if job:
			resp = message(True, "Analysis started")
			return resp, 200
		else:
			resp = err_resp(
					"Something went wrong. Couldn't start the workflow",
					"analysis_403",
					403,
				)
			return resp, 403
		

	@staticmethod
	def get_status(analysis_id):
		if analysis_id in AnalysisService.ANALYSIS:
			workflow = AnalysisService.ANALYSIS[analysis_id]
			response = workflow.status()
			return response,200
		else:
			return err_resp("Analysis not found!", "analysis_404", 404)
		
		