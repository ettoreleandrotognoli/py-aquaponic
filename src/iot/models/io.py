from __future__ import annotations
from django.core.cache import cache
from dataclasses import asdict
from django.forms.models import model_to_dict
import django.dispatch
from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import datetime, timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.utils.models import ValidateOnSaveMixin
from jsonfield import JSONField
from iot.actuators import ActuatorStrategy
from iot.actuators import SUPPORTED_STRATEGIES as ACTUATOR_STRATEGIES
from iot.fusion import FusionStrategy
from iot.fusion import SUPPORTED_FUSION_STRATEGIES as FUSION_STRATEGIES
from iot.fusion import FilterStrategy
from iot.fusion import SUPPORTED_FILTERS_STRATEGIES as FILTER_STRATEGIES
from iot.fusion import ConversionStrategy
from iot.fusion import SUPPORTED_CONVERSION_STRATEGIES as CONVERSION_STRATEGIES
from pydoc import locate
from iot.fusion import Sample
from iot.models.geo import Position

data_arrived = django.dispatch.Signal(providing_args=['data'])


class SensorDataQuerySet(models.QuerySet):
    def time_line(self, begin: datetime, end: datetime, interval: timedelta = timedelta(seconds=60 * 60)):
        if not isinstance(interval, timedelta):
            interval = timedelta(seconds=interval)
        current = begin
        while current < end:
            next_current = current + interval
            yield self.all().filter(
                timestamp__gte=current,
                timestamp__lt=next_current,
            )
            current = next_current

    def join(self):
        return self.aggregate(
            models.Avg('value'),
            models.Min('value'),
            models.Max('value'),
            models.Max('timestamp'),
            models.Min('timestamp'),
        )


class SensorDataManager(BaseManager.from_queryset(SensorDataQuerySet)):
    pass


class SensorData(ValidateOnSaveMixin, models.Model):

    objects = SensorDataManager()

    class Meta:
        verbose_name = _('Sensor Data')
        ordering = ('-timestamp',)

    objects = SensorDataQuerySet.as_manager()

    timestamp = models.DateTimeField(
        default=timezone.now
    )

    sensor = models.ForeignKey(
        'Sensor',
        related_name='data',
        on_delete=models.CASCADE,
    )

    measure_unit = models.ForeignKey(
        'MeasureUnit',
        related_name='data',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    position = models.ForeignKey(
        'Position',
        null=True,
        blank=True,
        related_name='data',
        on_delete=models.CASCADE,
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
            error_message = ugettext(
                'measure unit magnitude and sensor magnitude are different')
            raise ValidationError({'measure_unit': error_message})
        return super(SensorData, self).clean()

    @classmethod
    def from_sample(cls, sample: Sample) -> SensorData:
        return cls(
            position=Position.from_tuple(
                sample.position) if sample.position else None,
            value=sample.value,
            timestamp=sample.timestamp,
            measure_unit=sample.measure_unit,
        )

    def as_sample(self) -> Sample:
        return Sample(
            position=self.position.as_tuple() if self.position else None,
            value=self.value,
            timestamp=self.timestamp,
            measure_unit=self.measure_unit,
        )

    def __str__(self):
        return '%s %s' % tuple(map(str, (self.value, self.measure_unit if self.measure_unit_id else '?')))


class SensorQuerySet(models.QuerySet):
    pass


class SensorManager(BaseManager.from_queryset(SensorQuerySet)):
    pass


class Sensor(ValidateOnSaveMixin, models.Model):

    objects = SensorManager()

    class Meta:
        verbose_name = _('Sensor')
        ordering = ('name',)

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
        on_delete=models.CASCADE,
    )

    measure_unit = models.ForeignKey(
        'MeasureUnit',
        related_name='sensors',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    position = models.OneToOneField(
        'Position',
        related_name='sensor',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    is_virtual = models.BooleanField(
        default=False,
        verbose_name=_('It is a virtual sensor')
    )

    @property
    def cache_key(self):
        return 'sensor-{}'.format(self.pk)

    def set_value(self, value):
        self.push_data(value=value)

    def get_value(self):
        sample = self.get_last_data()
        return sample.value if sample else None

    def get_last_data(self) -> SensorData:
        last_sample = cache.get(self.cache_key)
        if last_sample:
            return last_sample
        last_data = self.data.order_by('-timestamp').first()
        if last_data:
            return last_data

    def set_last_data(self, data: SensorData):
        cache.set(self.cache_key, data)
        data_arrived.send_robust(sender=self.__class__, data=data)
        data.save()

    value = property(get_value, set_value)

    def clean(self):
        if self.measure_unit and self.measure_unit.magnitude != self.magnitude:
            error_message = ugettext(
                'measure unit magnitude and magnitude are different')
            raise ValidationError({
                'magnitude': error_message,
                'measure_unit': error_message,
            })
        return super(Sensor, self).clean()

    def init_data(self, **kwargs) -> SensorData:
        kwargs['sensor'] = self
        kwargs['timestamp'] = kwargs.get('timestamp', timezone.now())
        kwargs['position'] = kwargs.get('position', self.position)
        kwargs['measure_unit'] = kwargs.get('measure_unit', self.measure_unit)
        data = SensorData(**kwargs)
        return data

    def push_sample(self, sample: Sample):
        self.push_data(**asdict(sample))

    def push_data(self, **kwargs) -> SensorData:
        data = self.init_data(**kwargs)
        return self.set_last_data(data)

    def __str__(self):
        return '%s (%s)' % (self.name, self.magnitude.name)


class SensorFusionQuerySet(models.QuerySet):
    pass


class SensorFusionManager(BaseManager.from_queryset(SensorDataQuerySet)):
    pass


class SensorFusion(models.Model):

    objects = SensorFusionManager()

    class Meta:
        verbose_name = _('Sensor Fusion')
        ordering = ('output__name',)

    inputs = models.ManyToManyField(
        'Sensor',
        related_name='fusion_consumers',
    )

    output = models.OneToOneField(
        'Sensor',
        on_delete=models.CASCADE,
        verbose_name=_('Output sensor'),
        help_text=_('Output virtual sensor'),
        limit_choices_to={'is_virtual': True},
    )

    strategy = models.CharField(
        max_length=255,
        verbose_name=_('Fusion strategy'),
        choices=FUSION_STRATEGIES.items()
    )

    strategy_options = JSONField(
        null=True,
        blank=True,
        default={}
    )

    def load_strategy(self) -> FusionStrategy:
        fusion_strategy = locate(self.strategy)(**self.strategy_options)
        return fusion_strategy

    def input_changed(self, sensor_data: SensorData):
        merger = self.load_strategy()

        value, time, measure_unit = merger.merge(
            self.output, sensor_data, self.inputs.all())
        if value:
            self.output.push_data(value=value, time=time,
                                  measure_unit=measure_unit)


class SensorFilterQuerySet(models.QuerySet):
    pass


class SensorFilterManager(BaseManager.from_queryset(SensorFilterQuerySet)):
    pass


class SensorFilter(models.Model):

    objects = SensorFilterManager()

    class Meta:
        verbose_name = _('Sensor Filter')
        ordering = ('output__name',)

    strategy = models.CharField(
        max_length=255,
        verbose_name=_('Filter strategy'),
        choices=FILTER_STRATEGIES.items()
    )

    strategy_options = JSONField(
        null=True,
        blank=True,
        default={}
    )

    input = models.ForeignKey(
        'Sensor',
        related_name='filter_consumers',
        on_delete=models.CASCADE,
    )

    output = models.OneToOneField(
        'Sensor',
        on_delete=models.CASCADE,
        verbose_name=_('Output sensor'),
        help_text=_('Output virtual sensor'),
        limit_choices_to={'is_virtual': True},
    )

    def load_strategy(self) -> FilterStrategy:
        filter_strategy = locate(self.strategy)(**self.strategy_options)
        return filter_strategy

    def input_changed(self, data: SensorData):
        filter_strategy = self.load_strategy()
        sample_size = filter_strategy.sample_size()
        result = filter_strategy.filter(
            map(SensorData.as_sample, self.output.data.all()[:sample_size]),
            map(SensorData.as_sample, self.input.data.all()[:sample_size]),
        )
        self.output.push_sample(result)


class SensorConversionQuerySet(models.QuerySet):
    pass


class SensorConversionManager(BaseManager.from_queryset(SensorConversionQuerySet)):
    pass


class SensorConversion(models.Model):

    objects = SensorConversionManager()

    class Meta:
        verbose_name = _('Sensor Conversion')
        ordering = ('output__name',)

    strategy = models.CharField(
        max_length=255,
        verbose_name=_('Conversion strategy'),
        choices=CONVERSION_STRATEGIES.items()
    )

    strategy_options = JSONField(
        null=True,
        blank=True,
        default={}
    )

    inputs = models.ForeignKey(
        'Sensor',
        related_name='conversion_consumers',
        on_delete=models.CASCADE,
    )

    output = models.OneToOneField(
        'Sensor',
        on_delete=models.CASCADE,
        verbose_name=_('Output sensor'),
        help_text=_('Output virtual sensor'),
        limit_choices_to={'is_virtual': True},
    )


class ActuatorQuerySet(models.QuerySet):
    pass


class ActuatorManager(BaseManager.from_queryset(ActuatorQuerySet)):
    pass


class Actuator(models.Model):

    objects = ActuatorManager()

    class Meta:
        verbose_name = _('Actuator')
        ordering = ['name']

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
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    strategy = models.CharField(
        max_length=255,
        choices=ACTUATOR_STRATEGIES.items()
    )

    strategy_options = JSONField(
        null=True,
        blank=True,
        default={}
    )

    magnitude = models.ForeignKey(
        'Magnitude',
        on_delete=models.CASCADE,
    )

    measure_unit = models.ForeignKey(
        'MeasureUnit',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def load_strategy(self) -> ActuatorStrategy:
        actuator = locate(self.strategy)(**self.strategy_options)
        return actuator

    def set_value(self, value):
        device = self.load_strategy()
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
            try:
                return device.get_value()
            except NotImplementedError:
                pass
        data = self.data.all().order_by('-timestamp').first()
        if data:
            return data.value
        else:
            return 0

    value = property(get_value, set_value)

    def __str__(self):
        return self.name


class ActuatorDataQuerySet(models.QuerySet):
    pass


class ActuatorDataManager(BaseManager.from_queryset(ActuatorDataQuerySet)):
    pass


class ActuatorData(models.Model):

    objects = ActuatorDataManager()

    class Meta:
        verbose_name = _('Actuator Data')
        ordering = ('-timestamp',)

    timestamp = models.DateTimeField(
        default=timezone.now
    )

    actuator = models.ForeignKey(
        'Actuator',
        related_name='data',
        on_delete=models.CASCADE,
    )

    measure_unit = models.ForeignKey(
        'MeasureUnit',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    value = models.FloatField(

    )

    raw = JSONField(
        null=True,
        blank=True,
    )

    position = models.ForeignKey(
        'Position',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return '%s (%f)' % (self.actuator.name, self.value)
