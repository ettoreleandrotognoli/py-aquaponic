import json

from channels import Group as WSGroup
from core.utils.signals import try_signal, disable_for_loaddata
from django.db.models.signals import post_save
from django.dispatch import receiver
from iot.models import SensorData
from iot.models import Trigger


@receiver(post_save, sender=SensorData)
@disable_for_loaddata
@try_signal
def ws_update(instance, created, **kwargs):
    if not created:
        return
    ws_group = WSGroup('iot')
    data = json.dumps(dict(
        type='sensor-data',
        name=instance.sensor.name,
        endpoint=instance.sensor.endpoint,
        value=instance.value,
    ))
    ws_group.send(dict(text=data))


@receiver(post_save, sender=SensorData)
@disable_for_loaddata
@try_signal
def update_fusion(instance, created, **kwargs):
    if not created:
        return
    consumers = instance.sensor.consumers.all()
    for consumer in consumers:
        consumer.input_changed(instance)


@receiver(post_save, sender=SensorData)
@disable_for_loaddata
@try_signal
def update_pid(instance, created, **kwargs):
    if not created:
        return
    pid_controllers = instance.sensor.pid_controllers.all()
    for pid_controller in pid_controllers:
        pid_controller.input_changed(instance)


@receiver(post_save, sender=SensorData)
@disable_for_loaddata
@try_signal
def update_trigger(instance, created, **kwargs):
    if not created:
        return
    triggers = Trigger.objects.filter(conditions__input=instance.sensor, active=True)
    for trigger in triggers:
        trigger.try_fire()
