from typing import TypeVar
from typing import Tuple
from typing import Generic
from typing import Any
from typing import Iterable
from datetime import datetime
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

SUPPORTED_FUSION_STRATEGIES = {
    'iot.fusion.sampling.HighSampling': _('High Sampling'),
}

SUPPORTED_FILTERS_STRATEGIES = {
    'iot.fusion.filter.LowPass': _('Low Pass Filter'),
}

SUPPORTED_CONVERSION_STRATEGIES = {
    'iot.fusion.ldr.Lumen': _('Electric Tension to Lumen using a LDR'),
    'iot.fusion.ldr.Lux': _('Electric Tension to Lux using a LDR'),
    'iot.fusion.thermistor.SteinhartHart': _('Temperatude with Steinhart-Hart (NTC Thermistor) '),
    'iot.fusion.thermistor.BetaFactor': _('Temperatude with Beta Factor (NTC Thermistor) '),
}

E = TypeVar('E')


class Sample(Generic[E]):
    timestamp: datetime
    position: Tuple[float, float, float]
    value: E
    measure_unit: Any


class ConversionStrategy():
    def convert(self, sample: Sample) -> Sample:
        raise NotImplementedError()


class FilterStrategy(object):

    def sample_size(self) -> int:
        raise NotImplementedError()

    def filter(self, result_samples: Iterable[Sample], origin_samples: Iterable[Sample]) -> Sample:
        raise NotImplementedError()


class FusionStrategy(object):
    def merge(self) -> Any:
        raise NotImplementedError()
