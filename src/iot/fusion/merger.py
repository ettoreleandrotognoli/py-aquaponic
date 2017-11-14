from datetime import datetime
from typing import Iterable
from typing import Tuple

from iot.models import MeasureUnit
from iot.models import Sensor
from iot.models import SensorData


class Merger(object):
    def merge(self, output_sensor: Sensor, sensor_data: SensorData, sensors: Iterable[Sensor]) -> Tuple[float, datetime, MeasureUnit]:
        raise NotImplementedError()
