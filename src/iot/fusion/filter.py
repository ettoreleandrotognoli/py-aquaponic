from .merger import Merger


class LowPass(Merger):
    def __init__(self, high=1.0, low=2.0):
        self.high = high
        self.low = low

    def merge(self, output_sensor, sensor_data, sensors):
        last_value = output_sensor.data.order_by('-time').first()
        if not last_value:
            return sensor_data.value, sensor_data.time, sensor_data.measure_unit
        value = (sensor_data.value * self.high + last_value.value * self.low) / (self.high + self.low)
        return value, sensor_data.time, sensor_data.measure_unit
