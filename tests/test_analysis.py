

def test_new_analysis(client):

    data = {
        "analysis": {
            "id": "test"
        }
        "stream": {
            "type": "camera",
            "url": "https://www.youtube.com/watch?v=tk-qJJbdOh4",
            "resolution": "1080p",
            "sample_every" :30,
            "provider": "youtube",
            "length": 10
        },
        "workflow": {
            "name": "KAUST Fish Counter",
            "source_type": "stream"
        }
    }
    resp = client.post(
        "/api/analysis/",
        data=json.dumps(data),
        content_type="application/json",
    )
    assert resp.status_code == 201
    assert resp.json.get("message") == "Camera has been added"

    resp = client.get("/api/camera/", headers=headers)
    assert resp.json.get("camera")[0].get("name") == "dummy camera"
    assert resp.json.get("message") == "Camera data sent"
    assert resp.status_code == 200