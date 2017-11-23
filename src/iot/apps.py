from django.apps import AppConfig


class IotConfig(AppConfig):
    name = 'iot'

    def start_mqtt_data_sources(self):
        from .models import MQTTDataSource
        data_sources = MQTTDataSource.objects.filter(
            active=True,
            running=False,
        )
        for data_source in data_sources:
            data_source.send_update()

    def ready(self):
        from .signals import sensor_data
        from .signals import actuator_data
        from .signals import mqtt_data_source
        self.start_mqtt_data_sources()
