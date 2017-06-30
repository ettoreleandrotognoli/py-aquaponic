class Actuator(object):
    def set_value(self):
        raise NotImplementedError()


class ReadableActuator(Actuator):
    def set_value(self):
        raise NotImplementedError()

    def get_value(self):
        raise NotImplementedError()


class NullActuator(Actuator):
    def __init__(self, *args, **kwargs):
        pass

    def set_value(self):
        pass
