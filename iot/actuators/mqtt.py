import json

import paho.mqtt.publish as publish
from .actuator import Actuator


class MqttDevice(Actuator):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def set_value(self, value):
        kwargs = dict(self.kwargs)
        kwargs.update(dict(payload=json.dumps(value)))
        publish.single(
            **self.kwargs
        )
        return value
