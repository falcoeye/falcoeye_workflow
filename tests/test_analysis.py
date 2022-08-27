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
    busy = False
    for v in status.values():
        busy = busy or v
    return status,busy

def test_findfish_analysis(client,ta_fishfinder):

    data = {
        "analysis": {
            "id": "test_findfish_analysis",
            "async": True,
            "args": {
                "filename": f"{DIR}/../../media/arabian_angelfish_short.mp4",
                "sample_every": 30,
                "min_score_thresh": 0.30,
                "max_boxes": 30,
                "prefix": f"{DIR}/analysis/test_findfish_analysis/",
                "frequency": 3,
                "ntasks": 4
            }
        },
        "workflow": ta_fishfinder   
    }

    resp = client.post(
        "/api/analysis/",
        data=json.dumps(data),
        content_type="application/json",
    )
    logging.info(resp.json)
    assert resp.status_code == 200   

    status,busy = check_status(client,"test_findfish_analysis")
    logging.info(status)
    while busy:
        time.sleep(3)
        status,busy = check_status(client,"test_findfish_analysis")
        logging.info(status)

def test_grpc_findfish_analysis(client,ta_fishfinder_grpc):

    data = {
        "analysis": {
            "id": "test_grpc_findfish_analysis",
            "async": True,
            "args": {
                "filename": f"{DIR}/../../media/arabian_angelfish_short.mp4",
                "sample_every": 30,
                "min_score_thresh": 0.30,
                "max_boxes": 30,
                "prefix": f"{DIR}/analysis/test_grpc_findfish_analysis/",
                "frequency": 3,
                "ntasks": 4
            }
        },
        "workflow": ta_fishfinder_grpc   
    }

    resp = client.post(
        "/api/analysis/",
        data=json.dumps(data),
        content_type="application/json",
    )
    logging.info(resp.json)
    assert resp.status_code == 200   

    status,busy = check_status(client,"test_grpc_findfish_analysis")
    logging.info(status)
    while busy:
        time.sleep(3)
        status,busy = check_status(client,"test_grpc_findfish_analysis")
        logging.info(status)

def test_leaky_car_monitor_analysis(client,cars_monitor_leaky):

    data = {
        "analysis": {
            "id": "test_leaky_car_monitor",
            "async": True,
            "args": {
                "filename": "./tests/media/house_cars.mp4",
                "sample_every": 1,
                "min_score_thresh": 0.10,
                "max_boxes": 30,
                "min_to_trigger_in": 5,
                "min_to_trigger_out": 5,
                "prefix": "./tests/analysis/test_cut_video_segment/test_leaky_car_monitor",
                "length": 20,
                "frequency": 1,
                "timed_gate_open_freq": 30,
                "timed_gate_opened_last": 10
            }
        },
        "workflow": cars_monitor_leaky["structure"]  
    }

    resp = client.post(
        "/api/analysis/",
        data=json.dumps(data),
        content_type="application/json",
    )
    logging.info(resp.json)
    assert resp.status_code == 200   

    status,busy = check_status(client,"test_leaky_car_monitor")
    logging.info(status)
    while busy:
        time.sleep(3)
        status,busy = check_status(client,"test_leaky_car_monitor")
        logging.info(status)

def test_leaky_arabian_angelfish_analysis(client,arabian_angelfish_monitor_leaky):

    data = {
        "analysis": {
            "id": "test_leaky_arabian_angelfish",
            "async": True,
            "args": {
                "filename": "../../media/arabian_angelfish_short.mp4",
                "sample_every": 1,
                "min_score_thresh": 0.40,
                "max_boxes": 30,
                "min_to_trigger_in": 5,
                "min_to_trigger_out": 5,
                "prefix": "./tests/analysis/test_cut_video_segment/test_leaky_arabian_angelfish",
                "length": -1,
                "frequency": 1,
                "timed_gate_open_freq": 30,
                "timed_gate_opened_last": 5
            }
        },
        "workflow": arabian_angelfish_monitor_leaky["structure"]  
    }

    resp = client.post(
        "/api/analysis/",
        data=json.dumps(data),
        content_type="application/json",
    )
    logging.info(resp.json)
    assert resp.status_code == 200   

    status,busy = check_status(client,"test_leaky_arabian_angelfish")
    logging.info(status)
    while busy:
        time.sleep(3)
        status,busy = check_status(client,"test_leaky_arabian_angelfish")
        logging.info(status)

def test_leaky_arabian_angelfish_analysis_grpc(client,arabian_angelfish_monitor_leaky_grpc):

    data = {
        "analysis": {
            "id": "test_leaky_arabian_angelfish",
            "async": True,
            "args": {
                "filename": "../../media/arabian_angelfish_short.mp4",
                "sample_every": 1,
                "min_score_thresh": 0.40,
                "max_boxes": 30,
                "min_to_trigger_in": 5,
                "min_to_trigger_out": 5,
                "prefix": "./tests/analysis/test_cut_video_segment/test_leaky_arabian_angelfish",
                "length": -1,
                "frequency": 1,
                "timed_gate_open_freq": 30,
                "timed_gate_opened_last": 5
            }
        },
        "workflow": arabian_angelfish_monitor_leaky_grpc["structure"]  
    }

    resp = client.post(
        "/api/analysis/",
        data=json.dumps(data),
        content_type="application/json",
    )
    logging.info(resp.json)
    assert resp.status_code == 200   

    status,busy = check_status(client,"test_leaky_arabian_angelfish")
    logging.info(status)
    while busy:
        time.sleep(3)
        status,busy = check_status(client,"test_leaky_arabian_angelfish")
        logging.info(status)
