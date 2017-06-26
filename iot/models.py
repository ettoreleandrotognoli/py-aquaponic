from decimal import Decimal

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


class Sensor(models.Model):
    class Meta:
        verbose_name = _('Sensor')

    name = models.CharField(
        max_length=255,
        unique=True,
    )

    magnitude = models.ForeignKey(
        Magnitude,
        related_name='sensors',
    )

    position = models.OneToOneField(
        Position,
        related_name='sensor',
        null=True,
        blank=True
    )


class SensorData(models.Model):
    class Meta:
        verbose_name = _('Sensor Data')

    time = models.DateTimeField(
        default=timezone.now
    )

    sensor = models.ForeignKey(
        Sensor,
        related_name='datas',
    )

    measure_unit = models.ForeignKey(
        MeasureUnit,
        related_name='datas',
    )

    position = models.ForeignKey(
        Position,
        null=True,
        blank=True,
        related_name='datas',
    )

    value = JSONField(

    )

    raw = JSONField(
        null=True,
    )
