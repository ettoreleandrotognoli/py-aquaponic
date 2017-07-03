from core.utils.urls import make_url
from django.shortcuts import render
from iot.models import Actuator, Sensor, PID

urlpatterns = []

URL = make_url(urlpatterns)


@URL('^$')
def home(request):
    pid_list = PID.objects.all()
    actuator_list = Actuator.objects.all()
    sensor_list = Sensor.objects.all()
    return render(request, 'dashboard/charts.html', locals())
