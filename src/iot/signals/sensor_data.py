import json

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from core.utils.signals import safe_signal, disable_for_loaddata, thread_signal
from core.utils.signals import try_signal, disable_for_loaddata
from django.db.models.signals import post_save
from django.dispatch import receiver
from iot.models import SensorData
from iot.models import Trigger

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


# @receiver(post_save, sender=SensorData)
# @disable_for_loaddata
# @thread_signal
# @safe_signal
# def update_fusion(instance: SensorData, created, **kwargs):
#     if not created:
#         return
#     consumers = instance.sensor.consumers.all()
#     for consumer in consumers:
#         consumer.input_changed(instance)


# @receiver(post_save, sender=SensorData)
# @disable_for_loaddata
# @thread_signal
# @safe_signal
# def update_pid(instance: SensorData, created, **kwargs):
#     if not created:
#         return
#     pid_controllers = instance.sensor.pid_controllers.filter(active=True)
#     for pid_controller in pid_controllers:
#         pid_controller.input_changed(instance)


# @receiver(post_save, sender=SensorData)
# @disable_for_loaddata
# @thread_signal
# @safe_signal
# def update_trigger(instance: SensorData, created, **kwargs):
#     if not created:
#         return
#     triggers = Trigger.objects.filter(conditions__input=instance.sensor, active=True)
#     for trigger in triggers:
#         trigger.try_fire()
