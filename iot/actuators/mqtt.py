import paho.mqtt.client as mqtt


class MqttDevice(object):
    def __init__(self, topic, host, port=1883):
        self.topic = topic
        self.host = host
        self.port = port
        pass

    def set_value(self):
        pass

    def get_value(self):
        pass
