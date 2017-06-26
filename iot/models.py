from decimal import Decimal
from uuid import uuid4 as unique

import re
from django.db import models
from django.utils import timezone
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


class SensorData(models.Model):
    class Meta:
        verbose_name = _('Sensor Data')

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

    value = JSONField(

    )

    raw = JSONField(
        null=True,
    )

    def __str__(self):
        return '%s %s' % map(str, (self.value, self.measure_unit))


class Sensor(models.Model):
    class Meta:
        verbose_name = _('Sensor')

    name = models.CharField(
        max_length=255,
        unique=True,
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
        default=unique
    )

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
