class Actuator(object):
    def set_value(self, value: float) -> float:
        raise NotImplementedError()


class ReadableActuator(Actuator):
    def set_value(self, value: float) -> float:
        raise NotImplementedError()

    def get_value(self) -> float:
        raise NotImplementedError()


class ActuatorTemplate(Actuator):
    def prepare_value(self, value):
        return value

    def send_value(self, value):
        raise NotImplementedError()

    def set_value(self, value: float):
        value = self.prepare_value(value)
        self.send_value(value)
        return value


class LimitedActuator(ActuatorTemplate):
    def __init__(self, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value

    def prepare_value(self, value):
        prepared_value = value
        if self.max_value is not None:
            prepared_value = min(self.max_value, prepared_value)
        if self.min_value is not None:
            prepared_value = max(self.min_value, prepared_value)
        return prepared_value


class NullActuator(LimitedActuator):
    def __init__(self, *args, **kwargs):
        super(NullActuator, self).__init__(*args, **kwargs)

    def send_value(self, value):
        return value
