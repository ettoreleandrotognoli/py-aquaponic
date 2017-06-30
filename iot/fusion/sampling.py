from .merger import Merger


class HighSampling(Merger):
    def __init__(self, **kwargs):
        pass

    def merge(self, sensor_data, sensors):
        return sensor_data.value, sensor_data.time, sensor_data.measure_unit
