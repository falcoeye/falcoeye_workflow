from app.node.output import Output
import os
import cv2
import json
import logging
from app.utils import mkdir, put, random_string,tempdir,rm_file,exists
from datetime import datetime

class VideoWriter(Output):
    def __init__(self, name,prefix,frames_per_second=30):
        Output.__init__(self,name,prefix)
        self._prefix = prefix
        if self._prefix[-1] == "/":
            self._prefix = self._prefix[:-1]
        self._frames_per_second = frames_per_second
        self._writer = None
        self._meta = {
            "type": "media",
            "filenames": []
        }
        logging.info(f"Creating folder {prefix}")
        mkdir(prefix,self.context)

    def write_meta(self,context):
        metafile = f"{self._prefix}/meta.json" 
        logging.info(f"Creating meta data in {metafile}")
        with context.config["FS_OBJ"].open(
                os.path.relpath(metafile), "w"
            ) as f:
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

    def run(self,context=None):
        # expect dataframe object
        if context is None:
            context = self.context
        # TODO: refactor
        try:
            while self.more():
                logging.info(f"New video to write for {self._name}")
                count = 0
                item = self.get()
                self._meta["filenames"] = []

                filename = f"{self._prefix}/{self._name}_{count}.mp4"
                self._meta["filenames"].append(f'{self._name}_{count}.mp4')
                while exists(filename,context):
                    count += 1
                    filename = f'{self._prefix}/{self._name}_{count}.mp4'
                    self._meta["filenames"].append(f'{self._name}_{count}.mp4')
                
                logging.info(f"New video to write to {filename}")
            
                height,width,_ = item[0].size
                
                tempfile =  f'{tempdir()}/{datetime.now().strftime("%m_%d_%Y")}_{random_string()}.mp4'
                self.open_writer(tempfile,width,height)
                
                sorted_frames = sorted(item, key=lambda x: x.framestamp, reverse=False)
                for det in sorted_frames:
                    self._writer.write(det.frame_bgr)
                
                self.close_writer()
                
                put(tempfile,filename,context)
                rm_file(tempfile,context)

            self.write_meta(context)
        except Exception as e:
            logging.error(e)
    
