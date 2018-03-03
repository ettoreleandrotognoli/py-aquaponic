import json

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.utils.signals import safe_signal, disable_for_loaddata
from iot.models import ActuatorData

channel_layer = get_channel_layer()


@receiver(post_save, sender=ActuatorData)
@disable_for_loaddata
@safe_signal
def ws_update(instance, created, **kwargs):
    if not created:
        return
    data = json.dumps(dict(
        name=instance.actuator.name,
        endpoint=instance.actuator.endpoint,
        value=instance.value,
    ))
    async_to_sync(channel_layer.group_send)('iot.broadcast', dict(type='actuator_data', text=data))
