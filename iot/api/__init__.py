from .actuator import urlpatterns as actuator_url
from .sensor import urlpatterns as sensor_urls

urlpatterns = sensor_urls + actuator_url
