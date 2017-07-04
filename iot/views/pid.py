from core.utils.urls import make_url
from django import forms
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from iot.models import PID

urlpatterns = []

URL = make_url(urlpatterns)


class SetValueForm(forms.Form):
    target = forms.FloatField()


@URL('^pid/(?P<pk>\d+)/set/$', name='pid-set-target')
def set_value_view(request, **kwargs):
    pid = get_object_or_404(PID, **kwargs)
    form = SetValueForm(request.POST)
    if not form.is_valid():
        return redirect('iot:pid-list')
    pid.target = form.cleaned_data['target']
    pid.save()
    return redirect('iot:pid-list')


@URL('^pid/$', name='pid-list')
def list_view(request):
    pid_list = PID.objects.all().select_related(
        'input', 'output',
    )
    return render(request, 'pid/list.html', locals())
