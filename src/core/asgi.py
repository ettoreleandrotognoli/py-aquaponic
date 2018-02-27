from channels.routing import ProtocolTypeRouter
from channels.routing import URLRouter
from channels.http import AsgiHandler
from channels.routing import ChannelNameRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

from iot.routing import IoTWebSocketConsumer
from iot.routing import IoTConsumer

application = ProtocolTypeRouter({
    'http': AsgiHandler,
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path('', IoTWebSocketConsumer)
        ])
    ),
    'channel': ChannelNameRouter({
        'iot': IoTConsumer
    })
})
