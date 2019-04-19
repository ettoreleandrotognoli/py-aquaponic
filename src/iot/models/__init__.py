from .io import Sensor, SensorData, SensorFusion, SensorFilter, SensorConversion, Actuator, ActuatorData
from .mqtt import MQTTConnection, MQTTDataSource
from .control import PID
from .trigger import Trigger, TriggerAction, TriggerCondition
from .geo import Position
from .unit import Magnitude, MeasureUnit, ConversionFormula
from django.apps import apps


def generic_consumer(message):
    model = apps.get_model(message.content['model'])
    instance = model.objects.get(pk=message.content['pk'])
    method = getattr(instance, message.content['method'])
    method(*message.content['args'], **message.content['kwargs'])
