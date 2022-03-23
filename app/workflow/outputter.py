class Outputter:
    def __init__(self, name, ioHandler):
        self._ioHandler = ioHandler
        self._name = name

    def run(self):
        pass


class CalculationOutputter(Outputter):
    def __init__(self, name, ioHandler, calculation):
        Outputter.__init__(self, name, ioHandler)
        self._calculation = calculation

    def run(self):
        self._ioHandler.run(self._calculation.get_results())
