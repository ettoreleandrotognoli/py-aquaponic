from . import Sample
from typing import Sequence
from . import FusionStrategy


class HighSampling(FusionStrategy):
    def __init__(self, **kwargs):
        pass

    def merge(self, result_sample: Sample, origin_sample: Sample, others_sample: Sequence[Sample] ) -> Sample:
        return origin_sample
