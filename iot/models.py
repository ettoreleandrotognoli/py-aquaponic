from decimal import Decimal
from pydoc import locate
from uuid import uuid4 as unique

import re
from core.utils.models import ValidateOnSaveMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.timezone import timedelta
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField


class Magnitude(models.Model):
    class Meta:
        verbose_name = _('Magnitude')

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('Name'),
    )

    description = models.TextField(
        verbose_name=_('Description'),
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class MeasureUnit(models.Model):
    class Meta:
        verbose_name = _('Measure Unit')

    symbol = models.CharField(
        max_length=8,
        verbose_name=_('Symbol'),
    )

    name = models.CharField(
        max_length=255,
        verbose_name=_('Name'),
    )

    description = models.TextField(
        verbose_name=_('Description'),
        null=True,
        blank=True,
    )

    magnitude = models.ForeignKey(
        Magnitude,
        related_name='measures_units'
    )

    def __str__(self):
        return '%s (%s)' % (self.name, self.symbol)


class ConversionFormulaQuerySet(models.QuerySet):
    pass


class ConversionFormula(models.Model):
    DECIMAL_REGEX = re.compile(r'(\d+(.\d+)?)')

    class Meta:
        verbose_name = _('Conversion Formula')

    objects = ConversionFormulaQuerySet.as_manager()

    from_unit = models.ForeignKey(
        MeasureUnit,
        related_name='to_formulas',
    )

    to_unit = models.ForeignKey(
        MeasureUnit,
        related_name='from_formulas'
    )

    formula = models.TextField(

    )

    def prepare_formula(self, *args) -> str:
        formula = self.formula % args
        return self.DECIMAL_REGEX.sub(r"Decimal('\1')", formula)

    def convert_precisely(self, value) -> Decimal:
        return eval(self.prepare_formula(value))

    def convert_fast(self, value) -> float:
        return eval(self.formula % value)

    def __str__(self):
        return '%s ->  %s' % tuple(map(str, (self.from_unit, self.to_unit)))


class Position(models.Model):
    class Meta:
        verbose_name = _('Position')

    latitude = models.FloatField(
        verbose_name=_('Latitude'),
    )

    longitude = models.FloatField(
        verbose_name=_('Longitude'),
    )

    altitude = models.FloatField(
        verbose_name=_('Altitude'),
    )

    def __str__(self) -> str:
        return '%f° %f° %f' % (self.latitude, self.longitude, self.altitude)


class SensorData(ValidateOnSaveMixin, models.Model):
    class Meta:
        verbose_name = _('Sensor Data')
        ordering = ['-time']

    time = models.DateTimeField(
        default=timezone.now
    )

    sensor = models.ForeignKey(
        'Sensor',
        related_name='data',
    )

    measure_unit = models.ForeignKey(
        'MeasureUnit',
        related_name='data',
        null=True,
        blank=True,
    )

    position = models.ForeignKey(
        'Position',
        null=True,
        blank=True,
        related_name='data',
    )

    value = models.FloatField(
    )

    raw = JSONField(
        null=True,
        blank=True
    )

    def clean(self):
        if self.measure_unit_id is None:
            self.measure_unit = self.sensor.measure_unit
        if self.position_id is None:
            self.position = self.sensor.position
        if self.measure_unit and self.measure_unit.magnitude != self.sensor.magnitude:
            error_message = ugettext('measure unit magnitude and sensor magnitude are different')
            raise ValidationError({'measure_unit': error_message})
        return super(SensorData, self).clean()

    def __str__(self):

        return '%s %s' % tuple(map(str, (self.value, self.measure_unit if self.measure_unit_id else '?')))


class Sensor(ValidateOnSaveMixin, models.Model):
    class Meta:
        verbose_name = _('Sensor')

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('Name'),
    )

    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Description'),
    )

    magnitude = models.ForeignKey(
        'Magnitude',
        related_name='sensors',
    )

    measure_unit = models.ForeignKey(
        'MeasureUnit',
        related_name='sensors',
        null=True,
        blank=True,
    )

    position = models.OneToOneField(
        'Position',
        related_name='sensor',
        null=True,
        blank=True
    )

    endpoint = models.CharField(
        max_length=255,
        unique=True,
        default=unique,
        blank=True,
    )

    is_virtual = models.BooleanField(
        default=False,
        verbose_name=_('It is a virtual sensor')
    )

    def clean(self):
        if self.measure_unit and self.measure_unit.magnitude != self.magnitude:
            error_message = ugettext('measure unit magnitude and magnitude are different')
            raise ValidationError({
                'magnitude': error_message,
                'measure_unit': error_message,
            })
        return super(Sensor, self).clean()

    def init_data(self, **kwargs) -> SensorData:
        kwargs['sensor'] = self
        kwargs['time'] = kwargs.get('time', timezone.now())
        kwargs['position'] = kwargs.get('position', self.position)
        kwargs['measure_unit'] = kwargs.get('measure_unit', self.measure_unit)
        data = SensorData(**kwargs)
        return data

    def push_data(self, **kwargs) -> SensorData:
        data = self.init_data(**kwargs)
        data.save()
        return data

    def __str__(self):
        return '%s (%s)' % (self.name, self.magnitude.name)


class SensorFusion(models.Model):
    class Meta:
        verbose_name = _('Sensor Fusion')

    inputs = models.ManyToManyField(
        'Sensor',
        related_name='consumers',
    )

    output = models.OneToOneField(
        'Sensor',
        related_name='origin',
        verbose_name=_('Output sensor'),
        help_text=_('Output virtual sensor'),
    )

    strategy = models.CharField(
        max_length=255,
        verbose_name=_('Fusion strategy'),
        choices=(
            ('iot.fusion.sampling.HighSampling', _('High Sampling')),
        )

    )

    strategy_options = JSONField(
        null=True,
        blank=True,
        default={}
    )

    def input_changed(self, sensor_data: SensorData):
        merger = locate(self.strategy)(**self.strategy_options)
        value, time, measure_unit = merger.merge(sensor_data, self.inputs.all())
        if value:
            self.output.push_data(value=value, time=time, measure_unit=measure_unit)


class Actuator(models.Model):
    class Meta:
        verbose_name = _('Actuator')

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('Name')
    )

    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Description')
    )

    position = models.OneToOneField(
        'Position',
        related_name='actuator',
        null=True,
        blank=True
    )

    endpoint = models.CharField(
        max_length=255,
        unique=True,
        default=unique,
        blank=True,
    )

    strategy = models.CharField(
        max_length=255,
        choices=(
            ('iot.actuators.actuator.NullActuator', _('Null Actuator')),
            ('iot.actuators.parport.DataPin', _('Parallel Port Pin')),
        ),
    )

    strategy_options = JSONField(
        null=True,
        blank=True,
        default={}
    )

    magnitude = models.ForeignKey(
        'Magnitude',
    )

    measure_unit = models.ForeignKey(
        'MeasureUnit',
        null=True,
        blank=True,
    )

    def set_value(self, value):
        device = locate(self.strategy)(**self.strategy_options)
        data = ActuatorData(
            actuator=self,
            raw=value,
            value=device.set_value(value),
            measure_unit=self.measure_unit,
            position=self.position,
        )
        data.save()

    def get_value(self):
        device = locate(self.strategy)(**self.strategy_options)
        if hasattr(device, 'get_value'):
            return device.get_value()
        data = self.data.all().order_by('-time').first()
        if data:
            return data.value
        else:
            return None

    value = property(get_value, set_value)

    def __str__(self):
        return self.name


class ActuatorData(models.Model):
    time = models.DateTimeField(
        default=timezone.now
    )

    actuator = models.ForeignKey(
        'Actuator',
        related_name='data',
    )

    measure_unit = models.ForeignKey(
        'MeasureUnit',
        null=True,
        blank=True
    )

    value = models.FloatField(

    )

    raw = JSONField(
        null=True,
        blank=True,
    )

    position = models.ForeignKey(
        'Position',
        null=True,
        blank=True
    )

    def __str__(self):
        return '%s (%f)' % (self.actuator.name, self.value)


class PID(models.Model):
    class Meta:
        verbose_name = _('PID')

    name = models.CharField(
        max_length=255,
        unique=True,
    )

    active = models.BooleanField(
        default=True
    )

    input = models.ForeignKey(
        Sensor,
        related_name='pid_controllers'
    )

    output = models.ForeignKey(
        Actuator,
        related_name='pid_controllers'
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
        self.error = error
        self.save()
        self.output.set_value(p + i + d)

    def input_changed(self, sensor_data: SensorData):
        last = self.input.data.exclude(pk=sensor_data.pk).order_by('-time').first()
        interval = sensor_data.time - last.time if last else timedelta(seconds=0)
        self.update(sensor_data.value, interval)

    def __str__(self):
        return self.name
