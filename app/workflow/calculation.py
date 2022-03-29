import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

class TimestampRecorder:
    def __init__(self, name):
        self._name = name
        self._framestamps = []
        self._timestamps = []
        self._source_key = "video"

    def set_source(self, source):
        self._source_key = source

    def __call__(self, frame, results):

        if self._source_key == "video":
            self._framestamps.append(results.get_framestamp())

        self._timestamps.append(results.get_timestamp())

    def get_results(self):
        if self._source_key == "video":
            return {"frame": self._framestamps, "time": self._timestamps}
        elif self._source_key == "stream":
            return {"time": self._timestamps}

    @property
    def name(self):
        return self._name

    @classmethod
    def create(cls, **args):
        tr = TimestampRecorder(args["name"])
        if "source" in args:
            tr.set_source(args["source"])

        return tr

class DetectionRecorder:
    def __init__(self, name):
        self._name = name
        self._detections = []

    def __call__(self, frame, results):
        self._detections.append(results)

    def get_results(self):
        return self._detections

    @property
    def name(self):
        return self._name

    @classmethod
    def create(cls, **args):
        fr = DetectionRecorder(args["name"])
        return fr

class FramesRecorder:
    def __init__(self, name):
        self._name = name
        self._frames = []

    def __call__(self, frame, results):
        self._frames.append(frame)

    def get_results(self):
        return self._frames

    @property
    def name(self):
        return self._name

    @classmethod
    def create(cls, **args):
        fr = FramesRecorder(args["name"])
        return fr

class ObjectMonitor:
    def __init__(self, name, objectName, minToTriggerIn, minToTriggerOut):
        self._name = name
        self._objectName = objectName
        self._minToTriggerIn = minToTriggerIn
        self._minToTriggerOut = minToTriggerOut
        self._triggerCount = 0
        self._allowedToMiss = 2
        self._toMissCounter = 0
        self._status = 0  # 0 for out, 1 for in
        self._frames = []
        self._buffer = []
        self._triggeredOnce = False

    def __call__(self, frame, results):
        # out branch
        nobject = results.count_of(self._objectName)
        if self._status == 0:
            if (
                nobject <= 0
                and self._triggeredOnce
                and self._toMissCounter < self._allowedToMiss
            ):
                self._toMissCounter += 1
                print(f"Missed the object {self._toMissCounter}/{self._allowedToMiss}")
                return
            elif nobject <= 0:
                print(f"False alarm. Resetting")
                self._triggerCount = 0
                self._triggeredOnce = False
                self._toMissCounter = 0
                self._buffer = []
                return

            self._triggeredOnce = True
            self._triggerCount += 1
            self._toMissCounter = 0
            print(f"Found the object {self._triggerCount}")
            if self._triggerCount >= self._minToTriggerIn:
                print(f"Triggered in {len(self._frames)}")
                self._status = 1
                self._frames.append([f for f in self._buffer])
                self._buffer = []
                self._triggerCount = 0
            else:
                self._buffer.append(frame)
        # in branch
        elif self._status == 1:
            self._frames[-1].append(frame)
            if nobject <= 0:
                self._triggerCount += 1
            else:
                self._triggerCount = 0

            if self._triggerCount >= self._minToTriggerOut:
                print(f"Triggered out {len(self._frames)} with {len(self._frames[-1])}")
                self._status = 0
                self._triggerCount = 0
                self._triggeredOnce = False

    def get_results(self):
        return self._frames

    @property
    def name(self):
        return self._name

    @classmethod
    def create(cls, **args):
        minToTriggerIn = args.get("min_to_trigger_in", 5)
        minToTriggerOut = args.get("min_to_trigger_out", 5)
        objectName = args.get("object_name", None)
        if objectName is None:
            print(f"You must provide object name for object_monitor calculation")
            exit()
        fr = ObjectMonitor(args["name"], objectName, minToTriggerIn, minToTriggerOut)
        return fr

class TypeCounter:
    def __init__(self, name, keys):
        self._counts = {k: [] for k in keys}
        self._name = name

    def __call__(self, frame, results):
        for k in self._counts.keys():
            self._counts[k].append(results.count_of(k))

    def get_results(self):
        return self._counts

    @property
    def name(self):
        return self._name

    @classmethod
    def create(cls, **args):
        classes = args.get("class", None)
        if type(classes) == str:
            classes = [classes]
        elif not classes:
            print("Cannot create type counter without providing classes names")
            exit(0)

        tc = TypeCounter(args["name"], classes)
        return tc

class TypeFilter:
    def __init__(self, name, keys):
        self._ins = []
        self._keys = keys
        self._name = name

    def __call__(self, frame, results):
        ins = []
        for k in self._keys:
            ins += results.get_class_instances(k)
        self._ins.append(ins)

    def get_results(self):
        return self._ins

    @property
    def name(self):
        return self._name

    @classmethod
    def create(cls, **args):
        classes = args.get("class", None)
        if type(classes) == str:
            classes = [classes]
        elif not classes:
            print("Cannot create type counter without providing classes names")
            exit(0)

        tc = TypeFilter(args["name"], classes)
        return tc

class ZoneFilter:
    def __init__(self, points, width, height):
        self._points = points
        self._mask = Image.new("L", (width, height), 0)
        ImageDraw.Draw(self._mask).polygon(
            [tuple(x) for x in self._points], outline=1, fill=1
        )
        self._mask = np.array(self._mask).astype(bool)
        self._width, self._height = width, height
        self._ins = []

    def translate_pixel(self, x, y):
        return int(x * self._width), int(y * self._height)

    def __call__(self, frame, results):
        n = results.count()
        ins = []
        c = lambda x, y: self._mask[y, x]
        for i in range(n):
            ymin, xmin, ymax, xmax = results.get_box(i)
            xmin, ymin = self.translate_pixel(xmin * 0.9999, ymin * 0.9999)
            xmax, ymax = self.translate_pixel(xmax * 0.9999, ymax * 0.9999)
            if c(xmin, ymin) or c(xmin, ymax) or c(xmax, ymin) or c(xmax, ymax):
                ins.append(i)
        self._ins.append(ins)

    def get_results(self):
        return self._ins

    @property
    def name(self):
        return self._name

    @classmethod
    def create(cls, **args):
        points = args.get("points", None)
        width = args.get("width", None)
        height = args.get("height", None)

        zf = ZoneFilter(points, width, height)
        return zf

class CalculationsCalculation:
    def __init__(self, calculation_keys):
        self._calculation_keys = calculation_keys

    def keys(self):
        return self._calculation_keys

    def get_results(self):
        return

    def __call__(self):
        pass

class VisualizeDetectionOnFrames(CalculationsCalculation):
    def __init__(self, calculation_keys):
        CalculationsCalculation.__init__(self, calculation_keys)
        self._results = None

    def translate_pixel(self, x, y, width, height):
        return int(x * width), int(y * height)

    def __call__(self, calculations):
        # calculation values must have the same length
        framesCal = calculations[0]
        detectionCal = calculations[1]
        results = []
        frames = framesCal.get_results()
        height, width = frames[0].shape[:2]
        detections = detectionCal.get_results()
        color = (255, 0, 0)
        thickness = 2
        for f, det in zip(frames, detections):
            for d in det:
                ymin, xmin, ymax, xmax = d["box"]
                xmin, ymin = self.translate_pixel(xmin, ymin, width, height)
                xmax, ymax = self.translate_pixel(xmax, ymax, width, height)
                f = cv2.rectangle(f, (xmin, ymin), (xmax, ymax), color, thickness)
            results.append(f)
        self._results = results

    def get_results(self):
        return self._results

    @classmethod
    def create(self, **args):
        calkeys = args.get("calculations", None)
        if calkeys is None:
            print(
                f"You must provide calculation ids for visualize_detection_on_frames calculation"
            )
            exit()
        c = VisualizeDetectionOnFrames(calkeys)
        return c

class VisualizeZoneOnFrames(CalculationsCalculation):
    def __init__(self, calculation_keys, points, width, height):
        CalculationsCalculation.__init__(self, calculation_keys)
        self._results = None
        self._points = np.array(points).reshape((-1, 1, 2)).astype(np.int32)
        self._mask = np.zeros((height, width, 3))
        self._mask = cv2.drawContours(
            self._mask, [self._points], -1, color=(0, 0, 255), thickness=cv2.FILLED
        )

    def __call__(self, calculations):
        # calculation values must have the same length
        framesCal = calculations[0]
        results = []
        frames = framesCal.get_results()
        for f in frames:
            f = (f.astype(float) + 0.4 * self._mask).clip(0, 255).astype(np.uint8)
            results.append(f)
        self._results = results

    def get_results(self):
        return self._results

    @classmethod
    def create(self, **args):
        calkeys = args.get("calculations", None)
        points = args.get("points", None)
        width = args.get("width", None)
        height = args.get("height", None)
        if calkeys is None:
            print(
                f"You must provide calculation ids for visualize_detection_on_frames calculation"
            )
            exit()
        c = VisualizeZoneOnFrames(calkeys, points, width, height)
        return c

# class DetectionToText(CalculationsCalculation):
#     def __init__(self, calculation_keys,template):
#         CalculationsCalculation.__init__(self, calculation_keys)
#         self._results = None
#         self._template = template

#     def __call__(self, calculations):
#         # calculation values must have the same length
#         detectionCal = calculations[0]
#         results = []

#         for f,d in zip(frames,detections):
#             classd["class"]
#             xmin,ymin = self.translate_pixel(xmin,ymin,width,height)
#             xmax,ymax = self.translate_pixel(xmax,ymax,width,height)
#             results.append(cv2.rectangle(f, (xmin,ymin), (xmax,ymax), color, thickness))
#         self._results = results

#     def get_results(self):
#         return self._results

#     @classmethod
#     def create(self, **args):
#         calkeys = args.get("calculations", None)
#         template = args.get("template",None)
#         if calkeys is None:
#             print(f"You must provide calculation ids for detection_to_text calculation")
#             exit()
#         c = DetectionToText(calkeys)
#         return c

class DetectionOfFilter(CalculationsCalculation):
    def __init__(self, calculation_keys):
        CalculationsCalculation.__init__(self, calculation_keys)
        self._results = None

    def __call__(self, calculations):
        # calculation values must have the same length
        detectionsCal = calculations[0]
        filterCal = calculations[1]
        results = []
        detections = detectionsCal.get_results()
        filters = filterCal.get_results()
        for d, f in zip(detections, filters):
            results.append([])
            for i in f:
                fd = {"box": d.get_box(i), "class": d.get_class(i)}
                results[-1].append(fd)
        self._results = results

    def get_results(self):
        return self._results

    @classmethod
    def create(self, **args):
        calkeys = args.get("calculations", None)
        if calkeys is None:
            print(
                f"You must provide calculation ids for detection_of_filters calculation"
            )
            exit()
        c = DetectionOfFilter(calkeys)
        return c

class AndFilters(CalculationsCalculation):
    def __init__(self, calculation_keys):
        CalculationsCalculation.__init__(self, calculation_keys)
        self._results = None

    def __call__(self, calculations):
        # calculation values must have the same length
        results = []
        framesCount = len(calculations[0].get_results())
        for fr in range(framesCount):
            frameCal = set(calculations[0].get_results()[fr])
            for c in calculations[1:]:
                frameCal = frameCal & set(c.get_results()[fr])
            results.append(list(frameCal))
        self._results = results

    def get_results(self):
        return self._results

    @classmethod
    def create(self, **args):
        calkeys = args.get("calculations", None)
        if calkeys is None:
            print(f"You must provide calculation ids for and_filters calculation")
            exit()
        c = AndFilters(calkeys)
        return c

class CalculationsToDf(CalculationsCalculation):
    def __init__(self, calculation_keys):
        CalculationsCalculation.__init__(self, calculation_keys)
        self._df = None

    def __call__(self, calculations):
        # calculation values must have the same length
        data = {}
        for c in calculations:
            results = c.get_results()
            if type(results) == list:
                data[c.name] = results
            elif type(results) == dict:
                data.update(results)
        self._df = pd.DataFrame(data)

    def get_results(self):
        return self._df

    @classmethod
    def create(self, **args):
        calkeys = args.get("calculations", None)
        if calkeys is None:
            print(f"You must provide calculation ids for put_on_pd calculation")
            exit()
        c = CalculationsToDf(calkeys)
        return c
