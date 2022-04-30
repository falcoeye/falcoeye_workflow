
from app.node.node import Node

class ZoneFilter(Node):
    def __init__(self, name,points, width, height):
        Node.__init__(name)
        self._points = points
        self._mask = Image.new("L", (width, height), 0)
        ImageDraw.Draw(self._mask).polygon(
            [tuple(x) for x in self._points], outline=1, fill=1
        )
        self._mask = np.array(self._mask).astype(bool)
        self._width, self._height = width, height

    def translate_pixel(self, x, y):
        return int(x * self._width), int(y * self._height)

    def run(self):
        # expecting items of type FalcoeyeDetction
        while self.more():
            item = self.get()
            n = item.count()
            c = lambda x, y: self._mask[y, x]
            for i in range(n):
                ymin, xmin, ymax, xmax = item.get_box(i)
                xmin, ymin = self.translate_pixel(xmin * 0.9999, ymin * 0.9999)
                xmax, ymax = self.translate_pixel(xmax * 0.9999, ymax * 0.9999)
                if not (c(xmin, ymin) or c(xmin, ymax) or c(xmax, ymin) or c(xmax, ymax)):
                    item.delete(i)

            self.sink(self.item)


