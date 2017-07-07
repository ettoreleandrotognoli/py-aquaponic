from channels.routing import route
from iot.models import SensorData
from iot.models import Trigger


def update_fusion(message):
    sensor_data = SensorData.objects.filter(
        pk=message.content['sensor_data_pk']
    ).select_related('sensor').get()
    consumers = sensor_data.sensor.consumers.all()
    for consumer in consumers:
        consumer.input_changed(sensor_data)


def update_pid(message):
    sensor_data = SensorData.objects.filter(
        pk=message.content['sensor_data_pk']
    ).select_related('sensor').get()
    pid_controllers = sensor_data.sensor.pid_controllers.all()
    for pid_controller in pid_controllers:
        pid_controller.input_changed(sensor_data)


def update_trigger(message):
    sensor_data = SensorData.objects.filter(
        pk=message.content['sensor_data_pk']
    ).select_related('sensor').get()
    triggers = Trigger.objects.filter(conditions__input=sensor_data.sensor, active=True)
    for trigger in triggers:
        trigger.try_fire()


channel_routing = [
    route('iot.update_fusion', update_fusion),
    route('iot.update_pid', update_pid),
    route('iot.update_trigger', update_trigger),
]
