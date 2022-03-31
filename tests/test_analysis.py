import json
import time

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
    print(status,flush=True)
    while status["workflow_status"]:
        time.sleep(3)
        status = check_status(client,"test_stream")
        print(status,flush=True)

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
    print(resp.json,resp.status_code)
    assert resp.status_code == 200   

    status = check_status(client,"test_video")
    print(status,flush=True)
    while status["workflow_status"]:
        time.sleep(3)
        status = check_status(client,"test_video")
        print(status,flush=True)