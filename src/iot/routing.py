import json
from iot.models import SensorData
from iot.models import Trigger

from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from iot.models import SensorData
from iot.models import Trigger


class IoTWebSocketConsumer(AsyncJsonWebsocketConsumer):
    groups = 'iot.broadcast'

    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return
        await self.accept()
        await self.channel_layer.group_add(self.groups, self.channel_name)

    async def disconnect(self, code):
        if self.scope["user"].is_anonymous:
            return
        await self.channel_layer.group_discard(self.groups, self.channel_name)

    async def sensor_data(self, message):
        await self.send(message['text'])

    async def actuator_data(self, message):
        await self.send(message['text'])
        
def update_trigger(message):
    sensor_data = SensorData.objects.filter(
        pk=message.content['sensor_data_pk']
    ).select_related('sensor').get()
    triggers = Trigger.objects.filter(conditions__input=sensor_data.sensor, active=True)
    for trigger in triggers:
        trigger.try_fire()
