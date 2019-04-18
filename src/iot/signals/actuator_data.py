from django.db.models.signals import post_save
from django.dispatch import receiver
from iot.models import ActuatorData
from core.utils.signals import try_signal, disable_for_loaddata
import json


# @receiver(post_save, sender=ActuatorData)
# @disable_for_loaddata
# @try_signal
# def ws_update(instance, created, **kwargs):
#     if not created:
#         return
#     ws_group = WSGroup('iot')
#     data = json.dumps(dict(
#         type='actuator-data',
#         name=instance.actuator.name,
#         endpoint=instance.actuator.endpoint,
#         value=instance.value,
#     ))
#     ws_group.send(dict(text=data))
