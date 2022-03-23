import os

import pandas as pd


class CSVWriter:
    def __init__(self, filename):
        self._filename = filename

    def run(self, data):
        if type(data) == pd.DataFrame:
            CSVWriter.write_from_pandas(data, self._filename)

    @classmethod
    def write_from_pandas(cls, df, filename):
        df.to_csv(filename, index=False)

    @classmethod
    def create(cls, **args):
        filename = args.get("output_path", None)
        if filename is None:
            print("csv outputer requires to pass output_path")
            exit(0)
        filedir = os.path.dirname(filename)
        if not os.path.exists(filedir):
            print(f"The parent directory for {filename} doesn't exist")
            exit(0)
        return CSVWriter(filename)
