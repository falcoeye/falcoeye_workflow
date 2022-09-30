

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
import cv2



N=1

#url = "http://localhost:8501/v1/models/arabian_angelfish:predict"
MODEL_NAME ="cocoobjects" 

img = Image.open("../../media/jesr.jpeg")
width, height = img.size
print(width,height)
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
prediction = None
category_index = {3:"car"}
color = "red"

def non_max_suppression(boxes, probs, overlap_thresh):
    
    # if there are no boxes, return an empty list
    if boxes.shape[0] == 0:
        return []

    # if the bounding boxes are integers, convert them to floats -- this
    # is important since we'll be doing a bunch of divisions
    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float")

    # initialize the list of picked indexes
    pick = []

    # grab the coordinates of the bounding boxes
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    # compute the area of the bounding boxes and grab the indexes to sort
    # (in the case that no probabilities are provided, simply sort on the
    # bottom-left y-coordinate)
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = y2

    # if probabilities are provided, sort on them instead
    if probs is not None:
        idxs = probs

    # sort the indexes
    idxs = np.argsort(idxs).astype("int")

    # keep looping while some indexes still remain in the indexes list
    while len(idxs) > 0:
        # grab the last index in the indexes list and add the index value
        # to the list of picked indexes
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        # find the largest (x, y) coordinates for the start of the bounding
        # box and the smallest (x, y) coordinates for the end of the bounding
        # box
        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

        # compute the width and height of the bounding box
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        # compute the ratio of overlap
        overlap = (w * h) / area[idxs[:last]]
        print(overlap)
        # delete all indexes from the index list that have overlap greater
        # than the provided overlap threshold
        idxs = np.delete(idxs, np.concatenate(([last],
            np.where(overlap >= overlap_thresh)[0])))

    # return only the bounding boxes that were picked
    
    return pick

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
    global prediction
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
        classes = np.array(result.outputs['detection_classes'].float_val).astype(int)
        scores = np.array(result.outputs['detection_scores'].float_val)
        prediction = {'detection_boxes': boxes,
            'detection_classes':classes,
            'detection_scores': scores}

        

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

async def predict():
    global prediction
    tasks = []
    host = "localhost:5800"
    async with aio.insecure_channel(host, options=options) as channel:
    #async with aio.secure_channel(host, grpc.ssl_channel_credentials(), options=options) as channel:
        stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
        tasks.append(asyncio.create_task(post_grpc(pid=0,stub=stub)))
        await asyncio.gather(*tasks, return_exceptions=True)
    
    if prediction:
        boxes = prediction["detection_boxes"]
        boxes = boxes[:,[1,0,3,2]]
        classes = prediction['detection_classes']
        scores = prediction['detection_scores']
        
        delta = np.abs(boxes[:,0]-boxes[:,2])
        conf_mask = np.where(scores>0.01)
        
        boxes = boxes[conf_mask]
        classes = classes[conf_mask]
        scores = scores[conf_mask]

        nms_picks = non_max_suppression(
            boxes,scores,0.5
        )
        #nms_picks = range(0,classes.shape[0])
        lbl_img = img.copy()
        for counter,p in enumerate(nms_picks):
            if delta[p] > 0.1:
                continue
            if classes[p] in category_index.keys():
                class_name = str(category_index[classes[p]])
            else:
                class_name = "unknown"
            if class_name != "car":
                continue
            x1,y1,x2,y2 = boxes[p]
            x1,x2,y1,y2 = int(x1*width),int(x2*width),int(y1*height),int(y2*height)
            lbl_img = cv2.rectangle(lbl_img, (x1,y1), (x2,y2), (36,255,12), 1)
            cv2.putText(lbl_img, f"{class_name}{round(scores[p],2)}"  , 
                    (x1, y2-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 1)
            print(x1,y1,x2,y2,classes[p],class_name,scores[p])
            
        Image.fromarray(lbl_img).save("prediction.jpg")
            
            



start_time = time.time()
asyncio.run(predict())
grpctime = time.time() - start_time
print(f"GRPC Time {grpctime} ")



# start_time = time.time()
# asyncio.run(main_grpc())
# grpctime = time.time() - start_time

# start_time = time.time()
# asyncio.run(main_multiple_grpc())
# grpctime = time.time() - start_time
# print(f"GRPC Time {grpctime} ")

# start_time = time.time()
# asyncio.run(main())
# restime = time.time() - start_time

# print(f"GRPC Time {grpctime} REST Time {restime}")



