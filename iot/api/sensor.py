import pygal
from core.utils.urls import make_url
from core.utils.views import MultipleFieldLookupMixin, TrapDjangoValidationErrorMixin
from django.shortcuts import get_object_or_404
from iot.models import Sensor, SensorData
from iot.pygal import PygalViewMixin
from rest_framework.generics import ListAPIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from .serializers import SensorSerializer, SensorDetailSerializer, SensorDataSerializer

urlpatterns = []

URL = make_url(urlpatterns)


@URL('^sensor/$', name='sensor-list')
class SensorListView(ListCreateAPIView):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer


@URL('^sensor/(?P<endpoint>[^/]+)/$', name='sensor-detail')
@URL('^sensor/(?P<pk>[0-9]+)/$', name='sensor-detail')
class SensorDetailView(MultipleFieldLookupMixin,
                       TrapDjangoValidationErrorMixin,
                       RetrieveUpdateDestroyAPIView):
    lookup_field = ('pk', 'endpoint',)
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer

    serializers = {
        'GET': SensorDetailSerializer
    }

    def get_serializer_class(self):
        if not self.request:
            return self.serializer_class
        return self.serializers.get(self.request.method, self.serializer_class)


class SensorViewMixin(object):
    sensor = None

    def dispatch(self, request, *args, **kwargs):
        self.sensor = get_object_or_404(Sensor, **self.kwargs)
        return super(SensorViewMixin, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return SensorData.objects.filter(sensor=self.sensor).all()

    def perform_create(self, serializer):
        serializer.save(sensor=self.sensor)


@URL('^sensor-data/(?P<endpoint>[^/]+)/$', name='sensor-data')
@URL('^sensor-data/(?P<pk>[0-9]+)/$', name='sensor-data')
class SensorDataView(TrapDjangoValidationErrorMixin, SensorViewMixin, ListCreateAPIView):
    serializer_class = SensorDataSerializer


@URL('^sensor-chart/(?P<endpoint>[^/]+)/$', name='sensor-chart')
@URL('^sensor-chart/(?P<pk>[0-9]+)/$', name='sensor-chart')
class SensorChartView(PygalViewMixin, SensorViewMixin, ListAPIView):
    chart = pygal.DateTimeLine
    serializer_class = SensorDataSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        result = page or queryset
        chart = self.get_chart()
        chart.title = self.sensor.name
        chart.add(
            self.sensor.measure_unit.symbol if self.sensor.measure_unit else '?',
            [(sample.time, sample.value) for sample in result],
        )
        return chart.render_django_response()
