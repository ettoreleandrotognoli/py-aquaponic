from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.utils.signals import safe_signal, disable_for_loaddata
from iot.models import MQTTDataSource


@receiver(post_delete, sender=MQTTDataSource)
@disable_for_loaddata
@safe_signal
def on_delete(instance, **kwargs):
    instance.send_stop()


@receiver(post_save, sender=MQTTDataSource)
@disable_for_loaddata
@safe_signal
def on_update(instance, **kwargs):
    if instance.active:
        instance.send_update()
    else:
        instance.send_stop()
