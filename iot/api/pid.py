import pygal
from core.utils.urls import make_url
from core.utils.views import MultipleFieldLookupMixin, TrapDjangoValidationErrorMixin
from django.shortcuts import get_object_or_404
from iot.models import PID
from iot.pygal import PygalViewMixin
from rest_framework.generics import ListAPIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from .serializers import PIDSerializer, PIDDetailSerializer

urlpatterns = []

URL = make_url(urlpatterns)


@URL('^pid/$', name='pid-list')
class PIDListView(ListCreateAPIView):
    queryset = PID.objects.all()
    serializer_class = PIDSerializer


@URL('^pid/(?P<pk>[0-9]+)/$', name='pid-detail')
class PIDDetailView(MultipleFieldLookupMixin,
                    TrapDjangoValidationErrorMixin,
                    RetrieveUpdateDestroyAPIView):
    lookup_field = ('pk', 'endpoint',)
    queryset = PID.objects.all()
    serializer_class = PIDSerializer

    serializers = {
        'GET': PIDDetailSerializer
    }

    def get_serializer_class(self):
        if not self.request:
            return self.serializer_class
        return self.serializers.get(self.request.method, self.serializer_class)


class PIDViewMixin(object):
    pid = None

    def dispatch(self, request, *args, **kwargs):
        self.pid = get_object_or_404(PID.objects.select_related('input', 'output'), **self.kwargs)
        return super(PIDViewMixin, self).dispatch(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(pid=self.pid)


@URL('^pid-chart/(?P<pk>[0-9]+)/$', name='pid-chart')
class PIDChartView(PygalViewMixin, PIDViewMixin, ListAPIView):
    chart = pygal.DateTimeLine

    def get_output_data(self):
        return self.pid.output.data.all()

    def get_input_data(self):
        return self.pid.input.data.all()

    def list(self, request, *args, **kwargs):
        output_data_queryset = self.filter_queryset(self.get_output_data())
        output_data_page = self.paginate_queryset(output_data_queryset)
        output_data = output_data_page or output_data_queryset
        input_data_queryset = self.filter_queryset(self.get_input_data())
        input_data_page = self.paginate_queryset(input_data_queryset)
        input_data = input_data_page or input_data_queryset
        chart = self.get_chart()
        chart.title = self.pid.name
        chart.add(
            self.pid.input.measure_unit.symbol if self.pid.input.measure_unit else '?',
            [(sample.time, sample.value) for sample in input_data],
        )
        chart.add(
            self.pid.output.measure_unit.symbol if self.pid.output.measure_unit else '?',
            [(sample.time, sample.value) for sample in output_data],
            secondary=True
        )
        return chart.render_django_response()
