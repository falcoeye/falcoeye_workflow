

class DataFetcher:
    def __init__(self):
        pass
    def fetch(self):
        pass

class LocalStorageDataFetcher(DataFetcher):
    def __init__(self):
        DataFetcher.__init__(self)
    
    def fetch(self,data):
      
        framePath = data["frame"]
        resultsPath = data["results"]  
        img = Image.open(framePath)
        frame = np.asarray(img).copy()
        img.close()
        with open(resultsPath) as f2:
            results = json.load(f2)
        return frame,results
       