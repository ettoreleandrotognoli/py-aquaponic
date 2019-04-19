import re
from decimal import Decimal
from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

class MagnitudeQuerySet(models.QuerySet):
    pass


class MagnitudeManager(BaseManager.from_queryset(MagnitudeQuerySet)):
    pass


class Magnitude(models.Model):

    objects = MagnitudeManager()

    class Meta:
        verbose_name = _('Magnitude')
        ordering = ('name',)
        unique_together = (
            ('name',),
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

    def __str__(self):
        return self.name


class MeasureUnitQuerySet(models.QuerySet):
    pass


class MeasureUnitManager(BaseManager.from_queryset(MeasureUnitQuerySet)):
    pass


class MeasureUnit(models.Model):

    objects = MeasureUnitManager()

    class Meta:
        verbose_name = _('Measure Unit')
        ordering = ('name',)
        unique_together = (
            ('name',),
        )

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
        related_name='measures_units',
        on_delete=models.CASCADE,
    )

    def convert(self, value, unit):
        if self == unit:
            return value
        formula = ConversionFormula.objects.get(from_unit=unit, to_unit=self)
        return formula.convert_fast(value)

    def __str__(self):
        return '%s (%s)' % (self.name, self.symbol)


class ConversionFormulaQuerySet(models.QuerySet):
    pass


class ConversionFormulaManager(BaseManager.from_queryset(ConversionFormulaQuerySet)):
    pass


class ConversionFormula(models.Model):
    DECIMAL_REGEX = re.compile(r'(\d+(.\d+)?)')
    objects = ConversionFormulaManager()

    class Meta:
        verbose_name = _('Conversion Formula')
        ordering = ('from_unit__name', 'to_unit__name',)
        unique_together = (
            ('from_unit', 'to_unit',),
        )

    from_unit = models.ForeignKey(
        MeasureUnit,
        related_name='to_formulas',
        on_delete=models.CASCADE,
    )

    to_unit = models.ForeignKey(
        MeasureUnit,
        related_name='from_formulas',
        on_delete=models.CASCADE,
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
