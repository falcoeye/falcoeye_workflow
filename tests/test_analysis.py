import json
import time
def test_new_analysis(client,bank,factory):

    data = {
        "analysis": {
            "id": "test"
        },
        "stream": {
            "type": "stream",
            "url": "https://www.youtube.com/watch?v=ORz-rqB7Eno",
            "resolution": "1080p",
            "sample_every" :2,
            "provider": "youtube",
            "length": 60
        },
        "workflow": {
            "name": "KAUST Fish Counter",
            "model":{
                "name": "KAUST Fish Finder",
                "task": "detection",
                "framework": "tensorflow",
                "base_arch": "frcnn",
                "size": "1024",
                "deployment_path": "/Users/jalalirs/Documents/code/falcoeye/falcoeye_backbones/portofolio/fish/findfish/kaust_tf_frcnn_1024x1024/prod/",
                "deployment_type": "checkpoint"
            },
            "args": {
                "source_type":"stream",
                "output_path": "./a.csv"
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

    