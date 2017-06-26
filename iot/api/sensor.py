from core.utils import make_url
from iot.models import Sensor, SensorData
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView

urlpatterns = []

URL = make_url(urlpatterns)


class SensorSerializer(ModelSerializer):
    class Meta:
        model = Sensor
        fields = '__all__'


class SensorDataSerializer(ModelSerializer):
    class Meta:
        model = SensorData
        fields = '__all__'


@URL('^sensor/$', name='sensor-list')
class SensorListView(ListCreateAPIView):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer


@URL('^sensor/(?P<pk>)/$', name='sensor-detail')
class SensorDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer


@URL('^sensor/(?P<pk>)/data/$', name='sensor-data')
class SensorDataView(APIView):
    def post(self, request, format=None):
        serializer = SensorDataSerializer(data=request.data)
