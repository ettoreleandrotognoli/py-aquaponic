from typing import Iterator
from iot.models import SensorData


class MQTTDataSourceStrategy(object):
    def parse(self, *args, **kwargs) -> Iterator[SensorData]:
        raise NotImplementedError()


class JSONDataSourceStrategy(MQTTDataSourceStrategy):
    def parse(self):
        pass


class MQTTSingleTopicSensor(object):
    def __init__(self):
        pass
