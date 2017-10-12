import json

import paho.mqtt.publish as publish
from .actuator import LimitedActuator


class MqttDevice(LimitedActuator):
    def __init__(self, **kwargs):
        self.mqtt_kwargs = kwargs.pop('mqtt', {})
        super(MqttDevice, self).__init__(**kwargs)

    def send_value(self, value):
        kwargs = dict(self.mqtt_kwargs)
        kwargs.update(dict(payload=json.dumps(value)))
        publish.single(
            **kwargs
        )
        return value
