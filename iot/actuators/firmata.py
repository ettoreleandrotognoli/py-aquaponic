from .actuator import ActuatorTemplate
from channels import Channel


class FirmataPin(ActuatorTemplate):
    def __init__(self, pin):
        self.pin = pin

    def prepare_value(self, value):
        return min(max(0.0, value), 100.0)

    def send_value(self, value):
        Channel('firmata').send(dict(pin=self.pin, value=value/100.0), immediately=True)
