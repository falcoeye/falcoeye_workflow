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

def test_file_analysis(client,fishfinder):

    data = {
        "analysis": {
            "id": "test_video",
            "async": False,
            "args": {
                "filename": "../media/lutjanis.mov",
                "sample_every": 30,
                "min_score_thresh": 0.30,
                "max_boxes": 30,
                "prefix": "./tests/analysis/test_video/",
            }
        },
        "workflow": fishfinder   
    }

    resp = client.post(
        "/api/analysis/",
        data=json.dumps(data),
        content_type="application/json",
    )
    logging.info(resp.json)
    assert resp.status_code == 200   

    status,busy = check_status(client,"test_video")
    logging.info(status)
    while busy:
        time.sleep(3)
        status,busy = check_status(client,"test_video")
        logging.info(status)

def test_async_threaded_file_analysis(client,ta_fishfinder):

    data = {
        "analysis": {
            "id": "test_video_threaded_async",
            "async": True,
            "args": {
                "filename": "../media/arabian_angelfish_short.mov",
                "sample_every": 30,
                "min_score_thresh": 0.30,
                "max_boxes": 30,
                "prefix": "./tests/analysis/test_video_threaded_async/",
                "frequency": 3
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

    status,busy = check_status(client,"test_video_threaded_async")
    logging.info(status)
    while busy:
        time.sleep(3)
        status,busy = check_status(client,"test_video_threaded_async")
        logging.info(status)

def test_sequential_cut_video_segment_analysis(client,arabian_angelfish_sequential):

    data = {
        "analysis": {
            "id": "test_arabian_angelfish_sequential",
            "async": False,
            "args": {
                "filename": "./tests/media/arabian_angelfish_short.mov",
                "sample_every": 1,
                "min_score_thresh": 0.10,
                "max_boxes": 30,
                "min_to_trigger_in": 5,
                "min_to_trigger_out": 5,
                "prefix": "./tests/analysis/test_cut_video_segment/arabian_angelfish_sequential",
                "length": -1,
                "frequency": 1
            }
        },
        "workflow": arabian_angelfish_sequential   
    }

    resp = client.post(
        "/api/analysis/",
        data=json.dumps(data),
        content_type="application/json",
    )
    logging.info(resp.json)
    assert resp.status_code == 200   

    status,busy = check_status(client,"test_arabian_angelfish_sequential")
    logging.info(status)
    while busy:
        time.sleep(3)
        status,busy = check_status(client,"test_arabian_angelfish_sequential")
        logging.info(status)

def test_cut_video_segment_analysis(client,arabian_angelfish):

    data = {
        "analysis": {
            "id": "test_arabian_angelfish",
            "async": True,
            "args": {
                "filename": "./tests/media/arabian_angelfish_short.mov",
                "sample_every": 1,
                "min_score_thresh": 0.10,
                "max_boxes": 30,
                "min_to_trigger_in": 5,
                "min_to_trigger_out": 5,
                "prefix": "./tests/analysis/test_cut_video_segment/arabian_angelfish",
                "length": -1,
                "frequency": 1
            }
        },
        "workflow": arabian_angelfish   
    }

    resp = client.post(
        "/api/analysis/",
        data=json.dumps(data),
        content_type="application/json",
    )
    logging.info(resp.json)
    assert resp.status_code == 200   

    status,busy = check_status(client,"test_arabian_angelfish")
    logging.info(status)
    while busy:
        time.sleep(3)
        status,busy = check_status(client,"test_arabian_angelfish")
        logging.info(status)

def test_async_threaded_camera_analysis(client,ta_fishfinder):

    data = {
        "analysis": {
            "id": "test_camera_threaded_async",
            "async": True,
            "args": {
                "url": "https://www.youtube.com/watch?v=NwWgOilQuzw&t=4s",
                "resolution": "720p",
                "sample_every": 30,
                "min_score_thresh": 0.30,
                "max_boxes": 30,
                "length": 3,
                "prefix": "./tests/analysis/test_video_threaded_async/",
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

    status,busy = check_status(client,"test_camera_threaded_async")
    logging.info(status)
    while busy:
        time.sleep(3)
        status,busy = check_status(client,"test_camera_threaded_async")
        logging.info(status)

def test_camera_analysis(client,fishfinder):

    data = {
        "analysis": {
            "id": "test_camera",
            "async": False,
            "args": {
               "url": "https://www.youtube.com/watch?v=NwWgOilQuzw&t=4s",
                "resolution": "720p",
                "sample_every": 30,
                "min_score_thresh": 0.30,
                "max_boxes": 30,
                "length": 3,
                "prefix": "./tests/analysis/test_camera/",
            }
        },
        "workflow": fishfinder   
    }

    resp = client.post(
        "/api/analysis/",
        data=json.dumps(data),
        content_type="application/json",
    )
    logging.info(resp.json)
    assert resp.status_code == 200   

    # status,busy = check_status(client,"test_camera")
    # logging.info(status)
    # while busy:
    #     time.sleep(3)
    #     status,busy = check_status(client,"test_camera")
    #     logging.info(status)

def test_leaky_cut_video_segment_analysis(client,cars_monitor_leaky):

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
                "filename": "../media/arabian_angelfish_short.mp4",
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
