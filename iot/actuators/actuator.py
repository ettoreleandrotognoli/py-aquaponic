class Actuator(object):
    def set_value(self, value: float) -> float:
        raise NotImplementedError()


class ReadableActuator(Actuator):
    def set_value(self, value: float) -> float:
        raise NotImplementedError()

    def get_value(self) -> float:
        raise NotImplementedError()


class NullActuator(Actuator):
    def __init__(self, *args, **kwargs):
        pass

    def set_value(self, value: float) -> float:
        return value
