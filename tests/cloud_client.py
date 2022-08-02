


import requests



# data = {'analysis': {'id': 'cc68cbd3-9618-44ab-ad19-797b5482ff36', 'async': True, 'args': {'filename': 'falcoeye-bucket-test/user-assets/22689068-7c0e-45e0-8448-50d8489f051f/videos/cbf39036-7878-4aa3-826a-666acc04cd5a/video_original.mp4', 'sample_every': 30, 'min_score_thresh': 0.3, 'max_boxes': 30, 'prefix': 'falcoeye-bucket-test/user-assets/22689068-7c0e-45e0-8448-50d8489f051f/analysis/cc68cbd3-9618-44ab-ad19-797b5482ff36/', 'frequency': 3}}, 'workflow': {'args': [{'name': 'filename', 'type': 'string', 'disc': 'filepath for video in case of streaming from video file', 'source': 'infered', 'default': None}, {'name': 'url', 'type': 'string', 'disc': 'url for camera in case of streaming server', 'source': 'infered', 'default': None}, {'name': 'resolution', 'type': 'string', 'disc': 'resolution of streaming  in case of streaming server', 'source': 'user', 'default': 'best'}, {'name': 'host', 'type': 'string', 'disc': 'host for camera in case of rtsp camera', 'source': 'infered', 'default': None}, {'name': 'port', 'type': 'string', 'disc': 'port for camera in case of rtsp camera', 'source': 'infered', 'default': None}, {'name': 'username', 'type': 'string', 'disc': 'username for camera in case of rtsp camera', 'source': 'infered', 'default': None}, {'name': 'password', 'type': 'string', 'disc': 'password for camera in case of rtsp camera', 'source': 'infered', 'default': None}, {'name': 'sample_every', 'type': 'int', 'disc': 'Sample every (seconds for stream and frame for video)', 'source': 'user', 'default': 30}, {'name': 'min_score_thresh', 'type': 'float', 'disc': 'Minimum detection confidance ([0-1])', 'source': 'user', 'default': 0.5}, {'name': 'max_boxes', 'type': 'int', 'disc': 'Maximum number of detections ([0-100])', 'source': 'user', 'default': 100}, {'name': 'length', 'type': 'float', 'disc': 'Length of streaming (seconds, -1 for entire video)', 'source': 'user', 'default': -1}, {'name': 'frequency', 'type': 'int', 'disc': 'Output frequency (every n frame)', 'source': 'user', 'default': 3}], 'nodes': [{'name': 'stream_source', 'type': 'DynamicSource', 'filename': '$filename', 'url': '$url', 'host': '$host', 'port': '$port', 'username': '$username', 'password': '$password', 'length': '$length', 'sample_every': '$sample_every', 'resolution': '$resolution'}, {'name': 'findfish_model', 'type': 'TFObjectDetectionModel', 'model_name': 'findfish', 'version': 1}, {'name': 'findfish_model_thread', 'type': 'ConcurrentPostTasksThreadWrapper', 'node': 'findfish_model', 'tcplimit': 8}, {'name': 'falcoeye_detection', 'type': 'FalcoeyeDetectionNode', 'labelmap': {'1': 'fish'}, 'min_score_thresh': '$min_score_thresh', 'max_boxes': '$max_boxes'}, {'name': 'class_counter', 'type': 'ClassCounter', 'keys': ['fish']}, {'name': 'csv_outputter', 'type': 'CSVWriter', 'xaxis': 'Timestamp', 'yaxis': 'fish', 'prefix': '$prefix'}, {'name': 'sequence_runner', 'type': 'SequenceRunner', 'frequency': '$frequency', 'nodes': ['falcoeye_detection', 'class_counter', 'csv_outputter']}], 'edges': [['stream_source', 'findfish_model_thread'], ['falcoeye_detection', 'class_counter'], ['class_counter', 'csv_outputter'], ['findfish_model_thread', 'sequence_runner']], 'starters': ['stream_source'], 'run_order': ['sequence_runner', 'findfish_model_thread', 'stream_source']}}
data = {
    'analysis': 
    {
        'id': '0fcd6895-9cab-43c5-a90b-fd3c0f4bf995', 
        'async': True, 
        'args': {
            'filename': 'falcoeye-bucket-test/user-assets/22689068-7c0e-45e0-8448-50d8489f051f/videos/f703f16d-df06-4588-86f3-42d8d7346583/video_original.mp4', 
            'prefix': 'falcoeye-bucket-test/user-assets/22689068-7c0e-45e0-8448-50d8489f051f/analysis/0fcd6895-9cab-43c5-a90b-fd3c0f4bf995/', 
            "sample_every": 1,
            "min_score_thresh": 0.40,
            "max_boxes": 30,
            "min_to_trigger_in": 5,
            "min_to_trigger_out": 5,
            "length": -1,
            "frequency": 1,
            "timed_gate_open_freq": 30,
            "timed_gate_opened_last": 5,
            "tcplimit": 12
        }
    }, 
    'workflow': {
         "args": [
            {
                "name": "filename",
                "type": "string",
                "disc": "filepath for video in case of streaming from video file",
                "source": "infered",
                "default": None
            },
            {
                "name": "url",
                "type": "string",
                "disc": "url for camera in case of streaming server",
                "source": "infered",
                "default": None
            },
            {
                "name": "host",
                "type": "string",
                "disc": "host for camera in case of rtsp camera",
                "source": "infered",
                "default": None
            },
            {
                "name": "port",
                "type": "string",
                "disc": "port for camera in case of rtsp camera",
                "source": "infered",
                "default": None
            },
            {
                "name": "username",
                "type": "string",
                "disc": "username for camera in case of rtsp camera",
                "source": "infered",
                "default": None
            },
            {
                "name": "password",
                "type": "string",
                "disc": "password for camera in case of rtsp camera",
                "source": "infered",
                "default": None
            },
            {
                "name": "sample_every",
                "type": "int",
                "disc": "Sample every (seconds for stream and frame for video)",
                "source": "user",
                "default": 1
            },
            {
                "name": "min_score_thresh",
                "type": "float",
                "disc": "Minimum detection confidance ([0-1])",
                "source": "user",
                "default": 0.50
            },
            {
                "name": "max_boxes",
                "type": "int",
                "disc": "Maximum number of detections ([0-100])",
                "source": "user",
                "default": 100
            },
            {
                "name": "min_to_trigger_in",
                "type": "int",
                "disc": "Number of consecutive detections before start recording ([1-10])",
                "source": "user",
                "default": 5
            },
            {
                "name": "min_to_trigger_out",
                "type": "int",
                "disc": "Number of consecutive miss-detections before stop recording ([1-10])",
                "source": "user",
                "default": 5
            },
            {
                "name": "length",
                "type": "float",
                "disc": "Length of streaming (seconds, -1 for entire video)",
                "source": "user",
                "default": -1
            },
            {
                "name": "frequency",
                "type": "int",
                "disc": "Length of streaming (seconds, -1 for entire video)",
                "source": "user",
                "default": 5
            },
            {
                "name": "timed_gate_open_freq",
                "type": "int",
                "disc": "Frequency of opening timed gate in a leaky valve (i.e. every what frames?)",
                "source": "user",
                "default": 30
            },
            {
                "name": "timed_gate_opened_last",
                "type": "int",
                "disc": "Time the timed gate is kept open (i.e. after how many frames?) < timed_gate_open_freq",
                "source": "user",
                "default": 10
            },
            {
                "name": "tcplimit",
                "type": "int",
                "disc": "Number of tcp process at a time",
                "source": "user",
                "default": 4
            }
        ],
        "nodes": [
            {
                "name": "stream_source",
                "type": "DynamicSource",
                "filename": "$filename",
                "url": "$url",
                "host": "$host",
                "port": "$port",
                "username": "$username",
                "password": "$password",
                "length": "$length",
                "sample_every": "$sample_every"
            },
            {
                "name": "arabian_angelfish_model",
                "type": "TFObjectDetectionModel",
                "model_name": "arabian-angelfish",
                "version": 1
            },
            {
                "name": "arabian_angelfish_model_thread",
                "type": "ConcurrentPostTasksThreadWrapper",
                "node": "arabian_angelfish_model",
                "tcplimit": "$tcplimit"
            },
            {
                "name": "falcoeye_detection",
                "type": "FalcoeyeDetectionNode",
                "labelmap": {
                    "1": "arabian_angelfish"
                },
                "min_score_thresh": "$min_score_thresh",
                "max_boxes": "$max_boxes"
            },
            {
                "name": "sequence_maintainer",
                "type": "SortedSequence"
            },
            {
                "name": "leaky_valve",
                "type": "OneLeakyOneTimedValve",
                "timed_gate_open_freq": "$timed_gate_open_freq",
                "timed_gate_opened_last": "$timed_gate_opened_last",
                "nodes": ["sequence_maintainer","arabian_angelfish_model_thread"],
                "close_on_close": [False,True]
            },
            {
                "name": "arabian_angelfish_monitor",
                "type": "LeakyClasstMonitor",
                "object_name": "arabian_angelfish",
                "min_to_trigger_in": "$min_to_trigger_in",
                "min_to_trigger_out": "$min_to_trigger_out"
            },
            {
                "name": "video_writer",
                "type": "VideoWriter",
                "prefix": "$prefix"
            },
            {
                "name": "sequence_runner",
                "type": "SequenceRunner",
                "frequency": "$frequency",
                "nodes": [
                    "falcoeye_detection",
                    "sequence_maintainer",
                    "arabian_angelfish_monitor",
                    "video_writer"
                ]
            }
        ],
        "edges": [
            ["stream_source","leaky_valve"],
            ["falcoeye_detection","sequence_maintainer"],
            ["sequence_maintainer","arabian_angelfish_monitor"],
            ["arabian_angelfish_monitor","video_writer"],
            ["arabian_angelfish_model_thread","sequence_runner"]
        ],
        "starters":["stream_source"],
        "run_order": [
            "sequence_runner",
            "leaky_valve",
            "arabian_angelfish_model_thread",
            "stream_source"
        ]
    }
}



headers = {"accept": "application/json", "Content-Type": "application/json"}
            
wf_resp = requests.post(
    "https://falcoeye-workflow-xbjr6s7buq-uc.a.run.app/api/analysis/", json=data, headers=headers
)
print(wf_resp.status_code)
print(wf_resp.json())
