import logging

from functools import wraps


def disable_for_loaddata(signal_handler):
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get('raw'):
            return
        signal_handler(*args, **kwargs)

    return wrapper


def try_signal(signal_handler):
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        try:
            return signal_handler(*args, **kwargs)
        except Exception:
            logging.exception('Error on "%s" signal' % signal_handler.__name__)
            return None

    return wrapper
