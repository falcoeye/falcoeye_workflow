from flask import current_app

from app.utils import err_resp, internal_err_resp, message
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
		if not inline:
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
		else:
			# short job, create inline analysis then return
			jobname = random_string().lower()
			kube = FalcoJobKube(jobname,analysis_file)
			status = kube.start(watch=True) 
			logging.info(f"Job kube started for inline analysis {jobname}")
			if not status:
				resp = err_resp("inline analysis failed",
					"capture_403",
					403,
				)
				return resp, 403
			else:
				resp = message(True, "inline analysis succeded")
				return resp, 200
			

	@staticmethod
	def get_status(analysis_id):
		if analysis_id in AnalysisService.ANALYSIS:
			workflow = AnalysisService.ANALYSIS[analysis_id]
			response = workflow.status()
			return response,200
		else:
			return err_resp("Analysis not found!", "analysis_404", 404)
		
		