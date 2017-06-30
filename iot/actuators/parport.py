import parallel
from .actuator import ReadableActuator


class DataPin(ReadableActuator):
    def __init__(self, pin):
        self.parallel = parallel.Parallel()
        self.pin = pin % 8

    def set_value(self, value):
        data = self.parallel.getData()
        if value:
            data = data | (0x01 << self.pin)
        else:
            data = data & ~(0x01 << self.pin)
        self.parallel.setData(data)
        return 1 if value else 0

    def get_value(self):
        data = self.parallel.getData()
        return 1 if data & (0x01 << self.pin) else 0
