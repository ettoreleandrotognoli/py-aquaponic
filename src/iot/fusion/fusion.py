from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
from typing import Tuple
from typing import Any

@dataclass
class SensorData():
    value: float
    timestamp: datetime
    measure_unit: MeasureUnit

class FusionStrategy(object):
    def merge(self) -> Any:
        raise NotImplementedError()


class FilterStrategy(object):
    pass
