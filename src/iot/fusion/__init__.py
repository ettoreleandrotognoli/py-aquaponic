from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from .fusion import FusionStrategy
from .filter import FilterStrategy

SUPPORTED_STRATEGIES = {
    'iot.fusion.sampling.HighSampling': _('High Sampling'),
    'iot.fusion.ldr.Lumen': _('Electric Tension to Lumen using a LDR'),
    'iot.fusion.ldr.Lux': _('Electric Tension to Lux using a LDR'),
    'iot.fusion.thermistor.SteinhartHart': _(
        'Temperatude with Steinhart-Hart (NTC Thermistor) '),
    'iot.fusion.thermistor.BetaFactor': _(
        'Temperatude with Beta Factor (NTC Thermistor) '),
}

SUPPORTED_FILTERS = {
    'iot.fusion.filter.LowPass': _('Low Pass Filter'),
    'iot.fusion.filter.HighPass': _('High Pass Filter'),
}
