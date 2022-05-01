from app.node.node import Node
import os
import cv2

class VideoWriter(Node):
    def __init__(self, name,prefix,frames_per_second=30):
        Node.__init__(self,name)
        self._prefix = prefix
        self._frames_per_second = frames_per_second
        self._writer = None
    
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
        while self.more():
            count = 0
            item = self.get()
            
            while os.path.exists(f"{self._prefix}_{count}.mp4"):
                count += 1

            height,width,_ = item[0].size
            self.open(f'{self._prefix}_{count}.mp4',width,height)
            
            for det in item:
                self._writer.write(det.frame_bgr)
            
            self.close()