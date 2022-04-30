
from app.node.node import Node
import pandas as pd

class ClassCounter(Node):
    def __init__(self, name, keys):
        Node.__init__(self,name)
        self._keys = keys

    def run(self):
        table = []
        while self.more():
            item = self.get()
            row = [item.get_timestamp(),item.get_framestamp()]
            for k in self._keys:
                row.append(item.count_of(k))
            table.append(row)
        df = pd.DataFrame(table,columns=["Timestamp","Frame_Order"]+self._keys)
        self.sink(df)

