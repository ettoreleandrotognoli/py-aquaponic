from django.apps import AppConfig


class IotConfig(AppConfig):
    name = 'iot'

    def ready(self):
        from .signals import sensor_data
