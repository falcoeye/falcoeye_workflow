

import requests
from PIL import Image
import numpy as np 
import json
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from datetime import datetime
import time
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import asyncio
import aiohttp 
import grpc
import nsvision as nv
import tensorflow as tf
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc
from grpc import aio 



N=1

#url = "http://localhost:8501/v1/models/arabian_angelfish:predict"
MODEL_NAME ="cocoobjects" 

img = Image.open("../../media/fish2.jpg")
width, height = img.size
#img = img.resize((width//2, height//2))
img = np.asarray(img).astype(np.uint8)
instance = np.expand_dims(img, axis=0) 
data = json.dumps({"signature_name": "serving_default", "instances": instance.tolist()})
print(img.nbytes)
GRPC_MAX_RECEIVE_MESSAGE_LENGTH = 4096*4096*3
options = [
        ('grpc.max_send_message_length', GRPC_MAX_RECEIVE_MESSAGE_LENGTH),
        ('grpc.max_receive_message_length', GRPC_MAX_RECEIVE_MESSAGE_LENGTH),
        ('grpc.enable_http_proxy', 0),
]

async def post(session: aiohttp.ClientSession,pid:int):
    try:
        #url = "https://falcoeye-model-arabian-angelfish-xbjr6s7buq-uc.a.run.app/v1/models/arabian-angelfish:predict"
        url = f"http://localhost:8501/v1/models/{MODEL_NAME}:predict"
        headers = {"content-type": "application/json"}  
        print(f"Running {pid}")
        start_time = time.time()
        #print(data)
        response = await session.request("POST",url,headers=headers,data=data)
        responseText = await response.text()
        #print(responseText)
        predictions = json.loads(responseText)['predictions'][0]        
        print([a for a in predictions["detection_scores"] if a > 0.30])
        print(f"---{pid} done with time {time.time() - start_time}")
    except Exception as e:
        print(f'{pid} failed with {e}')

async def main():
    # Asynchronous context manager.  Prefer this rather
    # than using a different session for each GET request
    connector = aiohttp.TCPConnector(limit=N)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for i in range(N):
            tasks.append(post(session=session, pid=i))
        # asyncio.gather() will wait on the entire task set to be
        # completed.  If you want to process results greedily as they come in,
        # loop over asyncio.as_completed()
        await asyncio.gather(*tasks, return_exceptions=True)

async def post_grpc(pid,stub,model=None):
    try:
        start_time = time.time()
        
        request = predict_pb2.PredictRequest()
        if not model:
            model = MODEL_NAME
        
        print(f"Running {pid} {model}")
        request.model_spec.name = model

        # specify the serving signature from the model
        request.model_spec.signature_name = 'serving_default'
        request.inputs['input_tensor'].CopyFrom(tf.make_tensor_proto(instance))
        
        # retrieve the gRPC port from the context object
        # make a call that immediately and without blocking returns a 
        # gRPC future for the asynchronous-in-the-background gRPC.
        result = await stub.Predict(request)  # 5 seconds  
        #result = result.result()

        boxes = np.array(result.outputs['detection_boxes'].float_val).reshape((-1,4))
        classes = result.outputs['detection_classes'].float_val
        scores = result.outputs['detection_scores'].float_val
        print([s for s in scores if s >0.30])

        print(f"---{pid} done with time {time.time() - start_time}")
    except Exception as e:
        print(f'{pid} failed with {e}')

async def main_grpc():
    tasks = []
    host = "falcoeye-model-arabian-angelfish-grpc-xbjr6s7buq-uc.a.run.app:443"
    host = "localhost:8500"
    async with aio.insecure_channel(host, options=options) as channel:
    #async with aio.secure_channel(host, grpc.ssl_channel_credentials(), options=options) as channel:
        stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
        for i in range(N):
            tasks.append(asyncio.create_task(post_grpc(pid=i,stub=stub)))
        await asyncio.gather(*tasks, return_exceptions=True)

async def main_multiple_grpc():
    models = ["findfish","cocoobjects","arabian-angelfish"]
    tasks = []
    host = "falcoeye-model-arabian-angelfish-grpc-xbjr6s7buq-uc.a.run.app:443"
    host = "localhost:8500"
    async with aio.insecure_channel(host, options=options) as channel:
    #async with aio.secure_channel(host, grpc.ssl_channel_credentials(), options=options) as channel:
        stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
        for m in models:
            for i in range(N):
                tasks.append(asyncio.create_task(post_grpc(pid=i,stub=stub,model=m)))
        await asyncio.gather(*tasks, return_exceptions=True)

# start_time = time.time()
# asyncio.run(main_grpc())
# grpctime = time.time() - start_time

start_time = time.time()
asyncio.run(main_multiple_grpc())
grpctime = time.time() - start_time
print(f"GRPC Time {grpctime} ")

# start_time = time.time()
# asyncio.run(main())
# restime = time.time() - start_time

# print(f"GRPC Time {grpctime} REST Time {restime}")



