from .actuator import ActuatorTemplate


class FirmataPin(ActuatorTemplate):
    def __init__(self, pin):
        self.pin = pin

    def send_value(self, value):
        pass
