from django.urls import include, path

urlpatterns = [
    path('', include(('iot.views','iot-web',), namespace='iot')),
    path('api/', include(('iot.api','iot-api',), namespace='iot-api')),
]
