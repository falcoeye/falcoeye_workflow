

class FalcoeyeDetection:
    def __init__(self, detections, category_map):
        self._detections = detections
        self._category_map = category_map

    def count_of(self, category):
        if category in self._category_map:
            return len(self._category_map[category])
        return -1

    def get_boxes(self):
        return [d["box"] for d in self._detections]

    def get_class_instances(self, name):
        return [i for i, d in enumerate(self._detections) if d["class"] == name]

    def get_class(self, i):
        return self._detections[i]["class"]

    def get_classes(self):
        return [d["class"] for d in self._detections]

    def count(self):
        return len(self._detections)

    def get_box(self, i):
        return self._detections[i]["box"]


class FalcoeyeVideoDetection(FalcoeyeDetection):
    def __init__(self, detections, category_map, frame_number, relative_time):
        FalcoeyeDetection.__init__(self, detections, category_map)
        self._frame_number = frame_number
        self._relative_time = relative_time

    def get_framestamp(self):
        return self._frame_number

    def get_timestamp(self):
        return self._relative_time

