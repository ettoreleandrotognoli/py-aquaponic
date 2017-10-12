from .actuator import urlpatterns as actuator_urls
from .dashboard import urlpatterns as dashboard_urls
from .pid import urlpatterns as pid_urls
from .sensor import urlpatterns as sensor_urls

urlpatterns = sensor_urls + dashboard_urls + actuator_urls + pid_urls
