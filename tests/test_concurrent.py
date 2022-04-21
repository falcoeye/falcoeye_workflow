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

def test_concurrent(client,lutjanis,fishfinderw,fishfinderm):
    data = {
        "analysis": {
            "id": "test_concurrent"
        },
        "stream": lutjanis,
        "concurrent": True,
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
    assert resp.status_code == 200  
    
    status = check_status(client,"test_concurrent")
    logging.info(status)
    while status["workflow_status"]:
        time.sleep(3)
        status = check_status(client,"test_concurrent")
        logging.info(status)

