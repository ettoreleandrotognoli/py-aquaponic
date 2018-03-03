from channels.auth import AuthMiddlewareStack
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter
from channels.routing import URLRouter
from django.urls import path

from iot.routing import IoTWebSocketConsumer

application = ProtocolTypeRouter({
    'http': AsgiHandler,
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path('', IoTWebSocketConsumer)
        ])
    ),
})
