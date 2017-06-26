from django.conf.urls import url, include

urlpatterns = [
    url('', include('iot.views')),
    url('^api/', include('iot.api')),
]
