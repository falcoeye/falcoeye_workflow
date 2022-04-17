import json
import time
import os
import errno
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

DIR = os.path.dirname(os.path.realpath(__file__))


def check_status(client,analysis_id):
    resp = client.get(f"/api/analysis/status/{analysis_id}")
    assert resp.status_code == 200
    status = resp.json
    return status

def test_web_analysis(client,harbour,fishfinderw,fishfinderm):

    data = {
        "analysis": {
            "id": "test_stream"
        },
        "stream": harbour,
        "workflow": {
            "structure":fishfinderw,   
            "model":fishfinderm,
            "args": {
                "source_type":"stream",
                "output_path": "./tests/fishfinder_harbour.csv"
            }
        }
    }

    resp = client.post(
        "/api/analysis/",
        data=json.dumps(data),
        content_type="application/json",
    )
    assert resp.status_code == 200   

    status = check_status(client,"test_stream")
    logging.info(status)
    while status["workflow_status"]:
        time.sleep(3)
        status = check_status(client,"test_stream")
        logging.info(status)

def test_file_analysis(client,lutjanis,fishfinderw,fishfinderm):

    data = {
        "analysis": {
            "id": "test_video"
        },
        "stream": lutjanis,
        "workflow": {
            "structure":fishfinderw,   
            "model":fishfinderm,
            "args": {
                "source_type":"video",
                "output_path": "./tests/fishfinder_lutjanis.csv"
            }
        }
    }

    resp = client.post(
        "/api/analysis/",
        data=json.dumps(data),
        content_type="application/json",
    )
    logging.info(resp.json)
    assert resp.status_code == 200   

    status = check_status(client,"test_video")
    logging.info(status)
    while status["workflow_status"]:
        time.sleep(3)
        status = check_status(client,"test_video")
        logging.info(status)

def test_multilabel_analysis(client,vehicles,veheyew,veheyem):

    data = {
        "analysis": {
            "id": "test_multilabel"
        },
        "stream": vehicles,
        "workflow": {
            "structure":veheyew,   
            "model":veheyem,
            "args": {
                "source_type":"video",
                "output_path": "./tests/careye_veh.csv"
            }
        }
    }

    resp = client.post(
        "/api/analysis/",
        data=json.dumps(data),
        content_type="application/json",
    )
    logging.info(resp.json)
    assert resp.status_code == 200   

    status = check_status(client,"test_multilabel")
    logging.info(status)
    while status["workflow_status"]:
        time.sleep(3)
        status = check_status(client,"test_multilabel")
        logging.info(status)

def test_rtsp_camera(client,ezviz,humanw,humanm):
    data = {
        "analysis": {
            "id": "test_rtsp"
        },
        "stream": ezviz,
        "workflow": {
            "structure":humanw,   
            "model":humanm,
            "args": {
                "source_type":"stream",
                "output_path": "./tests/human.csv"
            }
        }
    }

    resp = client.post(
        "/api/analysis/",
        data=json.dumps(data),
        content_type="application/json",
    )
    logging.info(resp.json)
    assert resp.status_code == 200   

    status = check_status(client,"test_rtsp")
    logging.info(status)
    while status["workflow_status"]:
        time.sleep(3)
        status = check_status(client,"test_rtsp")
        logging.info(status)

def test_cut_video_segments(client,arabian_angelfish_short,fourtythreefishw,fourtythreefishm):

    data = {
        "analysis": {
            "id": "test_cut_video_segments"
        },
        "stream": arabian_angelfish_short,
        "workflow": {
            "structure":fourtythreefishw,   
            "model":fourtythreefishm,
            "args": {
                "source_type":"video",
                "output_prefix": "./tests/arabian_angelfish",
                "object_name" : "arabian_angelfish",
                "min_to_trigger_in": 5,
                "min_to_trigger_out": 5,
            }
        }
    }
    resp = client.post(
        "/api/analysis/",
        data=json.dumps(data),
        content_type="application/json",
    )
    logging.info(resp.json)
    assert resp.status_code == 200   

    status = check_status(client,"test_cut_video_segments")
    logging.info(status)
    while status["workflow_status"]:
        time.sleep(3)
        status = check_status(client,"test_cut_video_segments")
        logging.info(status)

def test_remote_cut_video_segments(client,arabian_angelfish_short,fourtythreefishw,fourtythreefishm):

    data = {
        "analysis": {
            "id": "remote_test_cut_video_segments"
        },
        "stream": arabian_angelfish_short,
        "remote_stream": True,
        "workflow": {
            "structure":fourtythreefishw,   
            "model":fourtythreefishm,
            "args": {
                "source_type":"video",
                "output_prefix": "./tests/arabian_angelfish",
                "object_name" : "arabian_angelfish",
                "min_to_trigger_in": 5,
                "min_to_trigger_out": 5,
            }
        }
    }
    resp = client.post(
        "/api/analysis/",
        data=json.dumps(data),
        content_type="application/json",
    )
    logging.info(resp.json)
    assert resp.status_code == 200   

    status = check_status(client,"remote_test_cut_video_segments")
    logging.info(status)
    while status["workflow_status"]:
        time.sleep(3)
        status = check_status(client,"remote_test_cut_video_segments")
        logging.info(status)

def test_remote_web_analysis(client,harbour,fishfinderw,fishfinderm):

    data = {
        "analysis": {
            "id": "test_remote_web_analysis"
        },
        "stream": harbour,
        "remote_stream": True,
        "workflow": {
            "structure":fishfinderw,   
            "model":fishfinderm,
            "args": {
                "source_type":"stream",
                "output_path": "./tests/fishfinder_harbour.csv"
            }
        }
    }

    resp = client.post(
        "/api/analysis/",
        data=json.dumps(data),
        content_type="application/json",
    )
    assert resp.status_code == 200   

    status = check_status(client,"test_remote_web_analysis")
    logging.info(status)
    while status["workflow_status"]:
        time.sleep(3)
        status = check_status(client,"test_remote_web_analysis")
        logging.info(status)

