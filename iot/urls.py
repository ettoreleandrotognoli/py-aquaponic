from django.conf.urls import url, include

urlpatterns = [
    url('', include('iot.views', namespace='iot')),
    url('^api/', include('iot.api', namespace='iot-api')),
]
