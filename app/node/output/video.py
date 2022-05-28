from app.node.output import Output
import os
import cv2
import json
import logging
class VideoWriter(Output):
    def __init__(self, name,prefix,frames_per_second=30):
        Output.__init__(self,name,prefix)
        self._prefix = prefix
        self._frames_per_second = frames_per_second
        self._writer = None
        self._meta = {
            "type": "media",
            "filenames": []
        }

    def write_meta(self):
        with open(f'{self._prefix}/meta.json',"w") as f:
            f.write(json.dumps(self._meta))

    def open_writer(self, filename,width, height):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self._writer = cv2.VideoWriter(
            filename,
            fourcc=fourcc,
            fps = 30,
            frameSize=(width, height),
            isColor=True,
        )
        logging.info(f"Writer for video {filename} opened")

    def close_writer(self):
        if self._writer:
            self._writer.release()

    def run(self):
        os.makedirs(self._prefix,exist_ok=True)
        self._meta["filenames"] = []
        while self.more():
            logging.info(f"New video to write for {self._name}")
            count = 0
            item = self.get()
            
            filename = f"{self._prefix}/{self._name}_{count}.mp4"
            self._meta["filenames"].append(filename)
            while os.path.exists(filename):
                count += 1
                filename = f'{self._prefix}/{self._name}_{count}.mp4'
                self._meta["filenames"].append(filename)
            
            logging.info(f"New video to write to {filename}")
        
            height,width,_ = item[0].size
            self.open_writer(filename,width,height)
            
            sorted_frames = sorted(item, key=lambda x: x.framestamp, reverse=False)
            for det in sorted_frames:
                self._writer.write(det.frame_bgr)
            
            self.close_writer()
        self.write_meta()
  
