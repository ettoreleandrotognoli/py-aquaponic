from django.views import View

from core.utils import make_url
from iot.models import Sensor
from django.shortcuts import get_object_or_404

urlpatterns = []

URL = make_url(urlpatterns)


# @URL('^sensor-chart/(?P<endpoint>[^/]+)/$', name='sensor-chart')
# @URL('^sensor-chart/(?P<pk>[0-9]+)/$', name='sensor-chart')
class SensorChartView(View):
    sensor = None

    def dispatch(self, request, *args, **kwargs):
        self.sensor = get_object_or_404(Sensor, **kwargs)
        return super(SensorChartView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        pass
