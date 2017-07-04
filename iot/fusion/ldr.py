from iot.models import MeasureUnit
from .merger import Merger

lux_unit = MeasureUnit.objetcs.get(name='lux')
lumen_unit = MeasureUnit.objects.get(name='lumen')


class Lux(Merger):
    def __init__(self, resistor=10000.0, tension=5.0, ldr_constant=500.0):
        self.resistor = resistor
        self.tension = tension
        self.ldr_constant = ldr_constant

    def merge(self, sensor_data, sensors):
        value = sensor_data.value
        lux = (self.tension * self.ldr_constant / value - self.ldr_constant) / (self.resistor / 1000.0)
        return lux, sensor_data.time, lux_unit


class Lumen(Merger):
    def __init__(self, resistor=10000.0, tension=5.0, ldr_constant=500.0, ldr_area=0.000025):
        self.resistor = resistor
        self.tension = tension
        self.ldr_constant = ldr_constant
        self.ldr_area = ldr_area

    def merge(self, sensor_data, sensors):
        value = sensor_data.value
        lux = (self.tension * self.ldr_constant / value - self.ldr_constant) / (self.resistor / 1000.0)
        lumen = lux * self.ldr_area
        return lumen, sensor_data.time, lumen_unit
