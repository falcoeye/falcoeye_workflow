
from app.node.node import Node
from PIL import ImageDraw, Image
import numpy as np
import logging
class ZoneFilter(Node):
    def __init__(self, name,points, width, height):
        Node.__init__(self,name)

        if type(points) == str:
            points = points.split(",")        
            points = [[int(points[i]),int(points[i+1])] for i in range(0,len(points),2)]
        
        logging.info(f"Creating zone filter around {points} with mask size {width} X {height}")
        self._points = points
        self._mask = Image.new("L", (width, height), 0)
        ImageDraw.Draw(self._mask).polygon(
            [tuple(x) for x in self._points], outline=1, fill=1
        )
        self._mask = np.array(self._mask).astype(bool)
        self._width, self._height = width, height

    def translate_pixel(self, x, y):
        return int(x * self._width), int(y * self._height)

    def run(self,context=None):
        # expecting items of type FalcoeyeDetction
        logging.info(f"Running {self.name}")
        while self.more():
            item = self.get()
            n = item.count
            c = lambda x, y: self._mask[y, x]
            # TODO: refactor to better deleting mechanism
            index = 0
            for i in range(n):
                ymin, xmin, ymax, xmax = item.get_box(index)
                xmin, ymin = self.translate_pixel(xmin * 0.9999, ymin * 0.9999)
                xmax, ymax = self.translate_pixel(xmax * 0.9999, ymax * 0.9999)
                if not (c(xmin, ymin) or c(xmin, ymax) or c(xmax, ymin) or c(xmax, ymax)):
                    item.delete(index)
                else:
                    # when deleting, no index increament due to shift in array
                    index += 1

            self.sink(item)


