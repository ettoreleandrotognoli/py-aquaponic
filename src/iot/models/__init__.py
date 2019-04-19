from django.apps import apps

def generic_consumer(message):
    model = apps.get_model(message.content['model'])
    instance = model.objects.get(pk=message.content['pk'])
    method = getattr(instance, message.content['method'])
    method(*message.content['args'], **message.content['kwargs'])


from .unit import Magnitude, MeasureUnit, ConversionFormula
from .geo import Position
from .io import Sensor, SensorData,SensorFusion, Actuator, ActuatorData
from .trigger import Trigger, TriggerAction, TriggerCondition
from .control import PID
from .mqtt import MQTTConnection, MQTTDataSource
