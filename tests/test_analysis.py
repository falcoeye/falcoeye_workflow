import json
import time
def test_new_analysis(client,bank,harbour,fishfinderw,fishfinderm):

    data = {
        "analysis": {
            "id": "test"
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
    status = client.get("/api/analysis/status/test").data.decode().replace("\"","").strip()
    while status == "running":
        status = client.get("/api/analysis/status/test").data.decode().replace("\"","").strip()
        print(status)
        time.sleep(3)

    