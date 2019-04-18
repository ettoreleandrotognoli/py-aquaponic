import json

from core.utils.signals import try_signal, disable_for_loaddata
from django.db.models.signals import post_save
from django.dispatch import receiver
from iot.models import SensorData


# @receiver(post_save, sender=SensorData)
# @disable_for_loaddata
# @try_signal
# def ws_update(instance, created, **kwargs):
#     if not created:
#         return
#     ws_group = WSGroup('iot')
#     data = json.dumps(dict(
#         type='sensor-data',
#         name=instance.sensor.name,
#         endpoint=instance.sensor.endpoint,
#         value=instance.value,
#     ))
#     ws_group.send(dict(text=data))


# @receiver(post_save, sender=SensorData)
# @disable_for_loaddata
# @try_signal
# def update_fusion(instance, created, **kwargs):
#     if not created:
#         return
#     Channel('iot.update_fusion').send(content=dict(
#         sensor_data_pk=instance.pk
#     ), immediately=True)


# @receiver(post_save, sender=SensorData)
# @disable_for_loaddata
# @try_signal
# def update_pid(instance, created, **kwargs):
#     if not created:
#         return
#     Channel('iot.update_pid').send(content=dict(
#         sensor_data_pk=instance.pk
#     ), immediately=True)


# @receiver(post_save, sender=SensorData)
# @disable_for_loaddata
# @try_signal
# def update_trigger(instance, created, **kwargs):
#     if not created:
#         return
#     Channel('iot.update_trigger').send(content=dict(
#         sensor_data_pk=instance.pk
#     ), immediately=True)
