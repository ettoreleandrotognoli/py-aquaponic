from decimal import Decimal
from pydoc import locate
from uuid import uuid4 as unique

import re
from core.utils.models import DecimalField
from core.utils.models import ValidateOnSaveMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
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

    latitude = DecimalField(
        verbose_name=_('Latitude'),
    )

    longitude = DecimalField(
        verbose_name=_('Longitude'),
    )

    altitude = DecimalField(
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
    )

    position = models.ForeignKey(
        'Position',
        null=True,
        blank=True,
        related_name='data',
    )

    value = DecimalField(
    )

    raw = JSONField(
        null=True,
        blank=True
    )

    def clean(self):
        if self.measure_unit.magnitude != self.sensor.magnitude:
            error_message = ugettext('measure unit magnitude and sensor magnitude are different')
            raise ValidationError({'measure_unit': error_message})
        return super(SensorData, self).clean()

    def __str__(self):
        return '%s %s' % tuple(map(str, (self.value, self.measure_unit)))


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
        if self.measure_unit.magnitude != self.magnitude:
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

    fusion_strategy = models.CharField(
        max_length=255,
        verbose_name=_('Fusion strategy')
    )

    def input_changed(self, sensor_data: SensorData):
        raise NotImplementedError()


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
            ('iot.parport.DataPin', _('Parallel Port Pin')),
        ),
    )

    strategy_options = JSONField(
        null=True,
        default={}
    )

    def set_value(self, value):
        device = locate(self.strategy)(**self.strategy_options)
        return device.set_value(value)

    def get_value(self):
        device = locate(self.strategy)(**self.strategy_options)
        return device.get_value()

    value = property(get_value, set_value)

    def __str__(self):
        return self.name


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

    target = DecimalField(

    )

    kp = DecimalField(

    )

    ki = DecimalField(

    )

    kd = DecimalField(

    )

    def input_changed(self, sensor_data: SensorData):
        raise NotImplementedError()

    def __str__(self):
        return self.name
