from .actuator import urlpatterns as actuator_url
from .pid import urlpatterns as pid_urls
from .sensor import urlpatterns as sensor_urls

urlpatterns = sensor_urls + actuator_url + pid_urls
