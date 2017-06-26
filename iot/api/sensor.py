from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.serializers import ModelSerializer

from core.utils import make_url, MultipleFieldLookupMixin, TrapDjangoValidationErrorMixin
from iot.models import Sensor, SensorData, Magnitude, MeasureUnit, Position

urlpatterns = []

URL = make_url(urlpatterns)


class MagnitudeSerializer(ModelSerializer):
    class Meta:
        model = Magnitude
        fields = ['id', 'name']


class MeasureUnitSerializer(ModelSerializer):
    class Meta:
        model = MeasureUnit
        fields = ['id', 'name', 'symbol']


class PositionSerializer(ModelSerializer):
    class Meta:
        model = Position
        exclude = ['id']


class SensorDetailSerializer(ModelSerializer):
    class Meta:
        model = Sensor
        fields = '__all__'

    magnitude = MagnitudeSerializer(many=False)
    measure_unit = MeasureUnitSerializer(many=False)
    position = PositionSerializer(many=False)


class SensorSerializer(ModelSerializer):
    class Meta:
        model = Sensor
        fields = '__all__'

    position = PositionSerializer(
        many=False,
        read_only=False,
        required=False,
    )

    def create(self, validated_data):
        position = validated_data.get('position', None)
        if position:
            position = PositionSerializer().create(position)
        validated_data['position'] = position
        return super(SensorSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        position = validated_data.pop('position', None)
        if position:
            position = PositionSerializer().create(position)
        instance.position = position
        return super(SensorSerializer, self).update(instance, validated_data)


class SensorDataSerializer(ModelSerializer):
    class Meta:
        model = SensorData
        exclude = ['sensor']


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


@URL('^sensor/(?P<endpoint>[^/]+)/data/$', name='sensor-data')
@URL('^sensor/(?P<pk>[0-9]+)/data/$', name='sensor-data')
class SensorDataView(TrapDjangoValidationErrorMixin, SensorViewMixin, ListCreateAPIView):
    serializer_class = SensorDataSerializer
