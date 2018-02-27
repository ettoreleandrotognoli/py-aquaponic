from iot.models import SensorData
import json
from iot.models import Trigger
from iot.models import generic_consumer
from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class IoTWebSocketConsumer(AsyncJsonWebsocketConsumer):
    groups = 'iot.broadcast'

    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            await self.accept()
        await self.channel_layer.group_add(self.groups, self.channel_name)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.groups, self.channel_name)

    async def sensor_data(self, message):
        await self.send(message['text'])

    async def actuator_data(self, message):
        await self.send(message['text'])


class IoTConsumer(AsyncConsumer):
    async def dispatch(self, message):
        message['content'] = json.loads(message['text'])
        await super().dispatch(message)

    async def update_fusion(self, event):
        sensor_data = SensorData.objects.filter(
            pk=event['content']['sensor_data_pk']
        ).select_related('sensor').get()
        consumers = sensor_data.sensor.consumers.all()
        for consumer in consumers:
            consumer.input_changed(sensor_data)

    async def update_pid(self, event):
        sensor_data = SensorData.objects.filter(
            pk=event['content']['sensor_data_pk']
        ).select_related('sensor').get()
        pid_controllers = sensor_data.sensor.pid_controllers.filter(active=True)
        for pid_controller in pid_controllers:
            pid_controller.input_changed(sensor_data)

    async def update_trigger(self, event):
        sensor_data = SensorData.objects.filter(
            pk=event['content']['sensor_data_pk']
        ).select_related('sensor').get()
        triggers = Trigger.objects.filter(conditions__input=sensor_data.sensor, active=True)
        for trigger in triggers:
            trigger.try_fire()


"""
channel_routing = [
    route('iot.update_fusion', update_fusion),
    route('iot.update_pid', update_pid),
    route('iot.update_trigger', update_trigger),
    route('iot.mqtt_data_source', generic_consumer),
]
"""
