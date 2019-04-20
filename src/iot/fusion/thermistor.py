import math

from iot.models import MeasureUnit
from .electronic import VoltageDivider
from . import ConversionStrategy
from . import Sample


def ln(value):
    return math.log(value, math.e)


class SteinhartHart(ConversionStrategy):
    """
    1/T = a + b*ln(R) + c* (ln(R))³
    """

    def __init__(self, a, b, c, resistor=10000, tension=5, proportional=True):
        self.kelvin_unit = MeasureUnit.objects.get(name='kelvin')
        self.a = a
        self.b = b
        self.c = c
        self.resistor = resistor
        self.tension = tension
        self.proportional = proportional

    def convert(self, sample: Sample) -> Sample:
        value = sample.value
        voltage_divider = VoltageDivider(vi=self.tension, vo=value)
        if self.proportional:
            voltage_divider.r2 = self.resistor
            r = voltage_divider.calc_r1()
        else:
            voltage_divider.r1 = self.resistor
            r = voltage_divider.calc_r2()
        t = 1.0 / (self.a + self.b * ln(r) + self.c * ln(r) ** 3)
        return Sample(
            timestamp=sample.timestamp,
            value=t,
            measure_unit=self.kelvin_unit,
            position=sample.position,
        )


class BetaFactor(ConversionStrategy):
    """
    1/T = 1/T0 + 1/B * ln(R/R0)
    """

    def __init__(self, b, t=298.15, r=10000, resistor=10000, tension=5, proportional=True):
        self.kelvin_unit = MeasureUnit.objects.get(name='kelvin')
        self.b = b
        self.t = t
        self.r = r
        self.resistor = resistor
        self.tension = tension
        self.proportional = proportional

    def convert(self, sample: Sample) -> Sample:
        value = sample.value
        voltage_divider = VoltageDivider(vi=self.tension, vo=value)
        if self.proportional:
            voltage_divider.r2 = self.resistor
            r = voltage_divider.calc_r1()
        else:
            voltage_divider.r1 = self.resistor
            r = voltage_divider.calc_r2()
        t = 1.0 / (1.0 / self.t + 1.0 / self.b * ln(r / self.r))
        return Sample(
            timestamp=sample.timestamp,
            value=t,
            measure_unit=self.kelvin_unit,
            position=sample.position,
        )
