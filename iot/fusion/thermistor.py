from .merger import Merger
import math
from .electronic import VoltageDivider
from iot.models import MeasureUnit

temperature_units = dict(
    [(unit.name, unit) for unit in MeasureUnit.objects.filter(magnitude__name='temperature')]
)


def ln(value):
    return math.log(value, math.e)


class SteinhartHart(Merger):
    """
    1/T = a + b*ln(R) + c* (ln(R))³
    """

    def __init__(self, a, b, c, resistor=10000, tension=5, output='kelvin', proportional=True):
        self.output = output
        self.a = a
        self.b = b
        self.c = c
        self.resistor = resistor
        self.tension = tension
        self.proportional = proportional

    def merge(self, output_sensor, sensor_data, sensors):
        value = sensor_data.value
        voltage_divider = VoltageDivider(vi=self.tension, vo=value)
        if self.proportional:
            voltage_divider.r2 = self.resistor
            r = voltage_divider.calc_r1()
        else:
            voltage_divider.r1 = self.resistor
            r = voltage_divider.calc_r2()
        t = 1.0 / (self.a + self.b * ln(r) + self.c * ln(r) ** 3)
        output_unit = temperature_units[self.output]
        t = output_unit.convert(t, temperature_units['kelvin'])
        return t, sensor_data.time, output_unit


class BetaFactor(Merger):
    """
    1/T = 1/T0 + 1/B * ln(R/R0)
    """

    def __init__(self, b, t=298.15, r=10000, resistor=10000, tension=5, output='kelvin', proportional=True):
        self.b = b
        self.t = t
        self.r = r
        self.resistor = resistor
        self.tension = tension
        self.output = output
        self.proportional = proportional

    def merge(self, output_sensor, sensor_data, sensors):
        value = sensor_data.value
        voltage_divider = VoltageDivider(vi=self.tension, vo=value)
        if self.proportional:
            voltage_divider.r2 = self.resistor
            r = voltage_divider.calc_r1()
        else:
            voltage_divider.r1 = self.resistor
            r = voltage_divider.calc_r2()
        t = 1.0 / (1.0 / self.t + 1.0 / self.b * ln(r / self.r))
        output_unit = temperature_units[self.output]
        t = output_unit.convert(t, temperature_units['kelvin'])
        return t, sensor_data.time, output_unit