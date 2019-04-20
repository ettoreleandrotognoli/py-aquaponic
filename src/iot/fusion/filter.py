from typing import Iterable
from . import Sample, FilterStrategy


class LowPass(FilterStrategy):
    def __init__(self, high=1.0, low=2.0):
        self.high = high
        self.low = low

    def sample_size(self):
        return 1

    def filter(self, result_samples: Iterable[Sample], origin_samples: Iterable[Sample]) -> Sample:
        last_origin = next(iter(origin_samples))
        try:
            last_result = next(iter(result_samples))
        except StopIteration:
            return last_origin
        value = (
            last_origin.value * self.high +
            last_result.value * self.low) / (self.high + self.low)
        return Sample(
            value=value,
            timestamp=last_origin.timestamp,
            measure_unit=last_origin.measure_unit,
            position=last_origin.position,
        )
