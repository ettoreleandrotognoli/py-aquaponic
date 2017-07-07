from channels.routing import route

from iot.consumers import ws_connect, ws_disconnect
from iot.routing import channel_routing as iot_routing

channel_routing = [
    route('websocket.connect', ws_connect),
    route('websocket.disconnect', ws_disconnect),
]

channel_routing += iot_routing
