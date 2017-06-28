import parallel


class DataPin(object):
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

    def get_value(self):
        data = self.parallel.getData()
        return data & (0x01 << self.pin)
