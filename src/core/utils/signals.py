import logging

from functools import wraps
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings

DEBUG = getattr(settings, 'DEBUG', False)
TESTING = getattr(settings, 'TESTING', False)

default_thread_pool = ThreadPoolExecutor(1 if DEBUG else multiprocessing.cpu_count() * 2)


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


def thread_signal(signal_handler, thread_poll=default_thread_pool):
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        thread_poll.submit(signal_handler, *args, **kwargs)

    return wrapper


if TESTING:
    thread_signal = lambda x: x
