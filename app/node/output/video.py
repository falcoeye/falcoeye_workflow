from app.node.output import Output
import os
import cv2
import json

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

    def open(self, filename,width, height):
        self._writer = cv2.VideoWriter(
            filename,
            fourcc=cv2.VideoWriter_fourcc(*"mp4v"),
            fps=self._frames_per_second,
            frameSize=(width, height),
            isColor=True,
        )

    def close(self):
        if self._writer:
            self._writer.release()

    def run(self):
        os.makedirs(self._prefix,exist_ok=True)
        self._meta["filenames"] = []
        while self.more():
            count = 0
            item = self.get()
            
            filename = f"{self._prefix}_{count}.mp4"
            self._meta["filenames"].append(filename)
            while os.path.exists(filename):
                count += 1
                filename = f'{self._prefix}_{count}.mp4'
                self._meta["filenames"].append(filename)
        
            height,width,_ = item[0].size
            self.open(filename,width,height)
            
            for det in item:
                self._writer.write(det.frame_bgr)
            
            self.close()
        self.write_meta()