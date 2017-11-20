import json
from typing import Iterator

from django.core.exceptions import ObjectDoesNotExist
from paho.mqtt import client as mqtt

from iot.models import Sensor
from iot.models import SensorData


class MQTTDataSourceStrategy(object):
    def parse(self, mqtt_client: mqtt.Client, userdata, msg) -> Iterator[SensorData]:
        raise NotImplementedError()


class JSONDataSourceStrategy(MQTTDataSourceStrategy):
    def __init__(self, encoding='utf-8'):
        self.encoding = encoding
        self.mqtt_client = None
        self.userdata = None
        self.msg = None

    def parse_data(self, topic, data) -> Iterator[SensorData]:
        raise NotImplementedError()

    def to_json(self, payload):
        return json.loads(payload.decode(self.encoding))

    def parse(self, mqtt_client: mqtt.Client, userdata, msg) -> Iterator[SensorData]:
        data = self.to_json(msg.payload)
        return self.parse_data(msg.topic, data)


class MQTTSingleTopicSensor(JSONDataSourceStrategy):
    def __init__(self, topic_index: int = -1, data_key: str = None):
        self.topic_index = topic_index
        self.data_key = data_key.split('.')

    def parse_data(self, topic, data) -> Iterator[SensorData]:
        sensor_name = topic.split('/')[self.topic_index]

        for key in self.data_key:
            data = data.get(key, {})
        if not data:
            return []
        try:
            sensor = Sensor.objects.get(name=sensor_name)
            return [sensor.init_data(value=data)]
        except ObjectDoesNotExist as ex:
            return []
