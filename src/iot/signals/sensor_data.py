import json

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from core.utils.signals import safe_signal, disable_for_loaddata, thread_signal
from django.db.models.signals import post_save
from django.dispatch import receiver
from iot.models import Sensor, SensorData
from iot.models import Trigger
from iot.models.io import data_arrived

channel_layer = get_channel_layer()


# @receiver(post_save, sender=SensorData)
# @disable_for_loaddata
# @safe_signal
# def ws_update(instance, created, **kwargs):
#     if not created:
#         return
#     data = json.dumps(dict(
#         name=instance.sensor.name,
#         endpoint=instance.sensor.endpoint,
#         value=instance.value,
#     ))
#     async_to_sync(channel_layer.group_send)('iot.broadcast', dict(type='sensor_data', text=data))


@receiver(data_arrived, sender=Sensor)
@thread_signal
@safe_signal
def update_fusion(data: SensorData, **kwargs):
    consumers = data.sensor.fusion_consumers.all()
    for consumer in consumers:
        consumer.input_changed(data)

@receiver(data_arrived, sender=Sensor)
@thread_signal
@safe_signal
def update_filter(data: SensorData, **kwargs):
    consumers = data.sensor.filter_consumers.all()
    for consumer in consumers:
        consumer.input_changed(data)


@receiver(data_arrived, sender=Sensor)
@thread_signal
@safe_signal
def update_conversion(data: SensorData, **kwargs):
    consumers = data.sensor.conversion_consumers.all()
    for consumer in consumers:
        consumer.input_changed(data)

@receiver(data_arrived, sender=Sensor)
@thread_signal
@safe_signal
def update_pid(data: SensorData, **kwargs):
    pid_controllers = data.sensor.pid_controllers.filter(active=True)
    for pid_controller in pid_controllers:
        pid_controller.input_changed(data)


@receiver(data_arrived, sender=Sensor)
@thread_signal
@safe_signal
def update_trigger(data: SensorData, **kwargs):
    triggers = Trigger.objects.filter(conditions__input=data.sensor, active=True)
    for trigger in triggers:
        trigger.try_fire()