import pygal
from django.template.defaultfilters import date as date_formater
from django import forms
from core.utils.urls import make_url
from core.utils.views import MultipleFieldLookupMixin, TrapDjangoValidationErrorMixin
from django.shortcuts import get_object_or_404
from django.utils import timezone
from iot.models import Sensor, SensorData
from iot.pygal import PygalViewMixin
from rest_framework.generics import ListAPIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from .serializers import SensorSerializer, SensorDetailSerializer, SensorDataSerializer

ISO8601 = "%Y-%m-%dT%H:%M:%S.%z"
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
        return self.sensor.data.all()

    def perform_create(self, serializer):
        serializer.save(sensor=self.sensor)


@URL('^sensor-data/(?P<endpoint>[^/]+)/$', name='sensor-data')
@URL('^sensor-data/(?P<pk>[0-9]+)/$', name='sensor-data')
class SensorDataView(TrapDjangoValidationErrorMixin, SensorViewMixin, ListCreateAPIView):
    serializer_class = SensorDataSerializer


@URL('^sample-sensor-chart/(?P<endpoint>[^/]+)/$', name='sample-sensor-chart')
@URL('^sample-sensor-chart/(?P<pk>[0-9]+)/$', name='sample-sensor-chart')
class SampleSensorChartView(PygalViewMixin, SensorViewMixin, ListAPIView):
    chart = pygal.DateTimeLine
    chart_options = {
        'x_value_formatter': lambda d: date_formater(d, 'SHORT_DATETIME_FORMAT')
    }
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


class SensorChartForm(forms.Form):
    begin = forms.DateTimeField(
        input_formats=[ISO8601],
        required=False,
    )

    end = forms.DateTimeField(
        input_formats=[ISO8601],
        required=False,
    )

    interval = forms.IntegerField(
        min_value=1,
        initial=60 * 60,
        required=False,
    )


@URL('^data-sensor-chart/(?P<endpoint>[^/]+)/$', name='sensor-chart')
@URL('^data-sensor-chart/(?P<pk>[0-9]+)/$', name='sensor-chart')
class SensorChartView(PygalViewMixin, SensorViewMixin, ListAPIView):
    chart = pygal.DateTimeLine
    chart_options = {
        'x_value_formatter': lambda d: date_formater(d, 'SHORT_DATETIME_FORMAT')
    }
    serializer_class = SensorDataSerializer
    interval = 60 * 60
    pagination_class = None

    def list(self, request, *args, **kwargs):
        form = SensorChartForm(data=request.GET)
        filter_data = {
            'begin': timezone.now() - timezone.timedelta(days=1),
            'end': timezone.now()
        }
        if form.is_valid():
            filter_data.update(filter(lambda kv: kv[1], form.clean().items()))
        result = self.get_queryset().time_line(**filter_data)
        chart = self.get_chart()
        chart.title = self.sensor.name
        symbol = self.sensor.measure_unit.symbol if self.sensor.measure_unit else '?'
        times = []
        values = {}
        for r in result:
            j = r.join()
            times.append(j['time__min'])
            for k, v in j.items():
                if not k.startswith('value__'):
                    continue
                if k not in values:
                    values[k] = []
                values[k].append(v)
        for k, v in values.items():
            chart.add("{} {}".format(k[7:], symbol), list(zip(times, v)))
        return chart.render_django_response()
