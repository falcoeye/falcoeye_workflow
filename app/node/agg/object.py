
from app.node.node import Node
import pandas as pd
import logging

class ClassCounter(Node):
    def __init__(self, name, keys):
        Node.__init__(self,name)
        self._keys = keys

    def run(self):
        table = []
        while self.more():
            item = self.get()
            row = [item.timestamp,item.framestamp]
            for k in self._keys:
                row.append(item.count_of(k))
            table.append(row)
        df = pd.DataFrame(table,columns=["Timestamp","Frame_Order"]+self._keys)
        self.sink(df)



class ClasstMonitor(Node):
    def __init__(self, name, object_name, min_to_trigger_in, min_to_trigger_out):
        Node.__init__(self,name)
        self._object_name = object_name
        self._min_to_trigger_in = min_to_trigger_in
        self._min_to_trigger_out = min_to_trigger_out
        
        self._triggered_once = False
        self._trigger_count = 0
        self._allowed_to_miss = 2
        self._to_miss_counter = 0
        self._status = 0  # 0 for out, 1 for in
        
        self._current_sequence = []
        self._buffer = []
        
    def run(self):
        while self.more():
            item = self.get()
            nobject = item.count_of(self._object_name)
            # Object is not yet in or not sufficiently in
            if self._status == 0:
                # Object was in in previous frame but perhaps missed prediction for this frame
                if nobject <= 0 and self._triggered_once and self._to_miss_counter < self._allowed_to_miss:
                    self._to_miss_counter += 1
                    continue
                # Object is "for sure" not in
                elif nobject <= 0:
                    self._triggerCount = 0
                    self._triggeredOnce = False
                    self._toMissCounter = 0
                    self._buffer = []
                    continue

                logging.info(f"{self._object_name} is found. Start peering")
                self._triggered_once = True
                self._trigger_count += 1
                self._to_miss_counter = 0
                # object is sufficiently in, so start monitoring
                if self._trigger_count >= self._min_to_trigger_in:
                    logging.info(f"{self._object_name} is sufficiently found. Start monitoring")
                    self._status = 1
                    self._current_sequence = [f for f in self._buffer]
                    self._buffer = []
                    self._trigger_count = 0
                # object is tentatively found. so add frame to buffer
                else:
                    self._buffer.append(item)
            
            # object is in 
            elif self._status == 1:
                self._current_sequence.append(item)
                # object is not in, so increase doubting that object is out
                if nobject <= 0:
                    self._trigger_count += 1
                else:
                    self._trigger_count = 0

                # Object is sufficiently out. So, finalize the recorded video
                if self._trigger_count >= self._min_to_trigger_out:
                    logging.info(f"{self._object_name} is out of scene. Stop monitoring")
                    self.sink(self._current_sequence)
                    self._current_sequence = []
                    self._status = 0
                    self._trigger_count = 0
                    self._triggered_once = False
        
        # in case stream finished while object is still in
        if len(self._current_sequence) > 0:
            self.sink(self._current_sequence)
            self._current_sequence = []
          
        