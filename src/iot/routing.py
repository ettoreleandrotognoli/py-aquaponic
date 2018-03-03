import json

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
