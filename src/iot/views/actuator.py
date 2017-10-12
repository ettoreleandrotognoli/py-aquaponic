from core.utils.urls import make_url
from django import forms
from django.db import models
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from iot.models import Actuator

urlpatterns = []

URL = make_url(urlpatterns)


class SetValueForm(forms.Form):
    value = forms.FloatField()


@URL('^actuator/(?P<pk>\d+)/set/$', name='actuator-set-value')
def set_value_view(request, **kwargs):
    actuator = get_object_or_404(Actuator, **kwargs)
    if actuator.pid_controllers.filter(active=True).count() > 0:
        return redirect('iot:actuator-list')
    form = SetValueForm(request.POST)
    if not form.is_valid():
        return redirect('iot:actuator-list')
    actuator.value = form.cleaned_data['value']
    return redirect('iot:actuator-list')


@URL('^actuator/$', name='actuator-list')
def list_view(request):
    actuator_list = Actuator.objects.all().annotate(
        pids=models.Count(models.Case(
            models.When(pid_controllers__active=True, then=1),
            models.When(pid_controllers__active=False, then=None),
        ))
    )
    return render(request, 'actuator/list.html', locals())
