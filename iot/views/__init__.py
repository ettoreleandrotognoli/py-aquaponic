from .dashboard import urlpatterns as dashboard_urls
from .sensor import urlpatterns as sensor_urls

urlpatterns = sensor_urls + dashboard_urls
