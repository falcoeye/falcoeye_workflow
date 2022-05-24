
from app.node.node import Node
from .stream import AngelCamSource,YoutubeSource,RTSPSource
from .video import VideoFileSource

def determine_source(**kwargs):
    url = kwargs.get("url", None)
    if url:
        if "youtube" in url:
            return YoutubeSource
        elif "angelcam" in url:
            return AngelCamSource
    filename = kwargs.get("filename", None) 
    if filename:
        return VideoFileSource
    
    return RTSPSource
    

class DynamicSource(Node):
    def __new__(cls,*args,**kwargs): 
        node_class = determine_source(**kwargs)
        return node_class(**kwargs)
    