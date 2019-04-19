from .fusion import FusionStrategy


class HighSampling(FusionStrategy):
    def __init__(self, **kwargs):
        pass

    def merge(self, output_sensor, sensor_data, sensors):
        return sensor_data.value, sensor_data.time, sensor_data.measure_unit
