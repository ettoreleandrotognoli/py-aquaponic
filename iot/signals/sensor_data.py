from django.db.models.signals import post_save
from django.dispatch import receiver
from iot.models import SensorData
from core.utils.signals import try_signal, disable_for_loaddata


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
