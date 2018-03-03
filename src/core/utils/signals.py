# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import logging

from functools import wraps


def disable_for_loaddata(signal_handler):
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get('raw'):
            return
        signal_handler(*args, **kwargs)

    return wrapper


def safe_signal(signal_handler):
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        try:
            return signal_handler(*args, **kwargs)
        except Exception as ex:
            logging.exception('Error on "%s" signal' % signal_handler.__name__)
            return None

    return wrapper
