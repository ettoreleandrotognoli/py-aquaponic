import json

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from core.utils.signals import try_signal, disable_for_loaddata
from django.db.models.signals import post_save
from django.dispatch import receiver
from iot.models import SensorData

channel_layer = get_channel_layer()


@receiver(post_save, sender=SensorData)
@disable_for_loaddata
@try_signal
def ws_update(instance, created, **kwargs):
    if not created:
        return
    data = json.dumps(dict(
        name=instance.sensor.name,
        endpoint=instance.sensor.endpoint,
        value=instance.value,
    ))
    async_to_sync(channel_layer.group_send)('iot.broadcast', dict(type='sensor_data', text=data))


@receiver(post_save, sender=SensorData)
@disable_for_loaddata
@try_signal
def update_fusion(instance, created, **kwargs):
    if not created:
        return
    data = json.dumps(dict(
        sensor_data_pk=instance.pk
    ))
    async_to_sync(channel_layer.send)('iot', dict(type='update_fusion', text=data))


@receiver(post_save, sender=SensorData)
@disable_for_loaddata
@try_signal
def update_pid(instance, created, **kwargs):
    if not created:
        return
    data = json.dumps(dict(
        sensor_data_pk=instance.pk
    ))
    async_to_sync(channel_layer.send)('iot', dict(type='update_pid', text=data))


@receiver(post_save, sender=SensorData)
@disable_for_loaddata
@try_signal
def update_trigger(instance, created, **kwargs):
    if not created:
        return
    data = json.dumps(dict(
        sensor_data_pk=instance.pk
    ))
    async_to_sync(channel_layer.send)('iot', dict(type='update_trigger', text=data))
