from __future__ import annotations

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import timedelta

from .io import SensorData, Sensor, Actuator


class PIDQuerySet(models.QuerySet):
    pass


class PIDManager(BaseManager.from_queryset(PIDQuerySet)):
    pass


class PID(models.Model):

    objects = PIDManager()

    class Meta:
        verbose_name = _('PID')
        ordering = ('-active', 'name',)

    name = models.CharField(
        max_length=255,
        unique=True,
    )

    active = models.BooleanField(
        default=True
    )

    inverse = models.BooleanField(
        default=False,
    )

    input = models.ForeignKey(
        Sensor,
        related_name='pid_controllers',
        on_delete=models.CASCADE,
    )

    output = models.ForeignKey(
        Actuator,
        related_name='pid_controllers',
        on_delete=models.CASCADE,
    )

    error = models.FloatField(
        default=0,
        null=False,
    )

    integral = models.FloatField(
        default=0,
        null=False,
    )

    target = models.FloatField(

    )

    kp = models.FloatField(

    )

    ki = models.FloatField(

    )

    kd = models.FloatField(

    )

    def set_value(self, value):
        self.target = value
        self.error = 0
        self.integral = 0
        self.save()

    def get_value(self):
        return self.target

    value = property(get_value, set_value)

    def _error_change(self, error):
        if self.error > 0 > error:
            return True
        if self.error < 0 < error:
            return True
        return False

    def update(self, feedback, interval: timedelta):
        error = self.target - feedback
        dt = interval.seconds
        self.integral += error * dt
        p = self.kp * error
        i = self.ki * self.integral
        if interval.seconds > 0:
            d = self.kd * (error - self.error) / dt
        else:
            d = 0
        if self._error_change(error):
            self.integral = 0
        self.error = error
        self.save()
        old_value = self.output.get_value()
        pid = p + i + d
        if self.inverse:
            new_value = old_value - pid
        else:
            new_value = old_value + pid
        self.output.set_value(new_value)

    def input_changed(self, sensor_data: SensorData):
        last = self.input.data.exclude(
            pk=sensor_data.pk
        ).order_by('-time').first()
        interval = sensor_data.time - last.time if last else timedelta(seconds=0)
        self.update(sensor_data.value, interval)

    def __str__(self):
        return self.name
