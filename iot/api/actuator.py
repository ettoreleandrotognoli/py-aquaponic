import pygal
from core.utils.urls import make_url
from core.utils.views import MultipleFieldLookupMixin, TrapDjangoValidationErrorMixin
from django.shortcuts import get_object_or_404
from iot.models import Actuator, ActuatorData
from iot.pygal import PygalViewMixin
from rest_framework.generics import ListAPIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from .serializers import ActuatorSerializer, ActuatorDetailSerializer, ActuatorDataSerializer

urlpatterns = []

URL = make_url(urlpatterns)


@URL('^actuator/$', name='actuator-list')
class ActuatorListView(ListCreateAPIView):
    queryset = Actuator.objects.all()
    serializer_class = ActuatorSerializer


@URL('^actuator/(?P<endpoint>[^/]+)/$', name='actuator-detail')
@URL('^actuator/(?P<pk>[0-9]+)/$', name='actuator-detail')
class ActuatorDetailView(MultipleFieldLookupMixin,
                         TrapDjangoValidationErrorMixin,
                         RetrieveUpdateDestroyAPIView):
    lookup_field = ('pk', 'endpoint',)
    queryset = Actuator.objects.all()
    serializer_class = ActuatorSerializer

    serializers = {
        'GET': ActuatorDetailSerializer
    }

    def get_serializer_class(self):
        if not self.request:
            return self.serializer_class
        return self.serializers.get(self.request.method, self.serializer_class)


class ActuatorViewMixin(object):
    actuator = None

    def dispatch(self, request, *args, **kwargs):
        self.actuator = get_object_or_404(Actuator, **self.kwargs)
        return super(ActuatorViewMixin, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return ActuatorData.objects.filter(actuator=self.actuator).all()

    def perform_create(self, serializer):
        serializer.save(actuator=self.actuator)


@URL('^actuator-data/(?P<endpoint>[^/]+)/$', name='actuator-data')
@URL('^actuator-data/(?P<pk>[0-9]+)/$', name='actuator-data')
class ActuatorDataView(TrapDjangoValidationErrorMixin, ActuatorViewMixin, ListAPIView):
    serializer_class = ActuatorDataSerializer


@URL('^actuator-chart/(?P<endpoint>[^/]+)/$', name='actuator-chart')
@URL('^actuator-chart/(?P<pk>[0-9]+)/$', name='actuator-chart')
class ActuatorChartView(PygalViewMixin, ActuatorViewMixin, ListAPIView):
    chart = pygal.DateTimeLine
    serializer_class = ActuatorDataSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        result = page or queryset
        chart = self.get_chart()
        chart.title = self.actuator.name
        chart.add(
            self.actuator.measure_unit.symbol if self.actuator.measure_unit else '?',
            [(sample.time, sample.value) for sample in result],
        )
        return chart.render_django_response()
