from iot.models import MeasureUnit
from .merger import Merger


class Lux(Merger):
    def __init__(self, resistor=10000.0, tension=5.0, ldr_constant=500000.0, light_proportional=True):
        self.resistor = resistor
        self.tension = tension
        self.ldr_constant = ldr_constant
        self.light_proportional = light_proportional
        self.lux_unit = MeasureUnit.objects.get(name='lux')

    def merge(self, output_sensor, sensor_data, sensors):
        value = sensor_data.value
        if self.light_proportional:
            lux = (value * self.ldr_constant) / (self.resistor * (self.tension - value))
        else:
            lux = (self.tension * self.ldr_constant - self.ldr_constant) / (value * self.resistor)
        return lux, sensor_data.time, self.lux_unit


class Lumen(Lux):
    def __init__(self, ldr_area=0.000025, **kwargs):
        super(Lumen, self).__init__(**kwargs)
        self.ldr_area = ldr_area
        self.lumen_unit = MeasureUnit.objects.get(name='lumen')

    def merge(self, sensor_data, sensors):
        lux, time, unit = super(Lumen, self).merge(sensor_data, sensors)
        lumen = lux * self.ldr_area
        return lumen, time, self.lumen_unit
