from iot.models import MeasureUnit
from .conversion import ConversionStrategy
from . import Sample


class Lux(ConversionStrategy):
    def __init__(self, resistor=10000.0, tension=5.0, ldr_constant=500000.0, light_proportional=True):
        self.resistor = resistor
        self.tension = tension
        self.ldr_constant = ldr_constant
        self.light_proportional = light_proportional
        self.lux_unit = MeasureUnit.objects.get(name='lux')

    def convert(self, sample: Sample) -> Sample:
        value = sample.value
        if self.light_proportional:
            lux = (
                (value * self.ldr_constant) /
                (self.resistor * (self.tension - value))
            )
        else:
            lux = (
                (self.tension * self.ldr_constant - self.ldr_constant) /
                (value * self.resistor)
            )
        return Sample(
            timestamp=sample.timestamp,
            value=lux,
            measure_unit=self.lux_unit
        )


class Lumen(Lux):
    def __init__(self, ldr_area=0.000025, **kwargs):
        super(Lumen, self).__init__(**kwargs)
        self.ldr_area = ldr_area
        self.lumen_unit = MeasureUnit.objects.get(name='lumen')

    def convert(self, sample: Sample) -> Sample:
        lux_sample = super().convert(sample)
        lumen = lux_sample.value * self.ldr_area
        return Sample(
            timestamp=sample.timestamp,
            value=lumen,
            measure_unit=self.lumen_unit
        )
