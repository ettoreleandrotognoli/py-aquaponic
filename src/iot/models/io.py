from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import datetime, timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.utils.models import ValidateOnSaveMixin
from jsonfield import JSONField
from pydoc import locate

class SensorDataQuerySet(models.QuerySet):
    def time_line(self, begin: datetime, end: datetime, interval: timedelta = timedelta(seconds=60 * 60)):
        if not isinstance(interval, timedelta):
            interval = timedelta(seconds=interval)
        current = begin
        while current < end:
            next_current = current + interval
            yield self.all().filter(
                time__gte=current,
                time__lt=next_current,
            )
            current = next_current

    def join(self):
        return self.aggregate(
            models.Avg('value'),
            models.Min('value'),
            models.Max('value'),
            models.Max('time'),
            models.Min('time'),
        )


class SensorDataManager(BaseManager.from_queryset(SensorDataQuerySet)):
    pass

class SensorData(ValidateOnSaveMixin, models.Model):

    objects = SensorDataManager()

    class Meta:
        verbose_name = _('Sensor Data')
        ordering = ('-time',)

    objects = SensorDataQuerySet.as_manager()

    time = models.DateTimeField(
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

    def set_value(self, value):
        self.push_data(value=value)

    def get_value(self):
        last_data = self.data.order_by('-time').first()
        if not last_data:
            return None
        return last_data.value

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
        related_name='consumers',
    )

    output = models.OneToOneField(
        'Sensor',
        related_name='origin',
        on_delete=models.CASCADE,
        verbose_name=_('Output sensor'),
        help_text=_('Output virtual sensor'),
        limit_choices_to={'is_virtual': True},
    )

    strategy = models.CharField(
        max_length=255,
        verbose_name=_('Fusion strategy'),
        choices=(
            ('iot.fusion.sampling.HighSampling', _('High Sampling')),
            ('iot.fusion.ldr.Lumen', _('Electric Tension to Lumen using a LDR')),
            ('iot.fusion.ldr.Lux', _('Electric Tension to Lux using a LDR')),
            ('iot.fusion.thermistor.SteinhartHart', _(
                'Temperatude with Steinhart-Hart (NTC Thermistor) ')),
            ('iot.fusion.thermistor.BetaFactor', _(
                'Temperatude with Beta Factor (NTC Thermistor) ')),
            ('iot.fusion.filter.LowPass', _('Low Pass Filter')),
            ('iot.fusion.filter.HighPass', _('High Pass Filter')),
        )

    )

    strategy_options = JSONField(
        null=True,
        blank=True,
        default={}
    )

    def input_changed(self, sensor_data: SensorData):
        merger = locate(self.strategy)(**self.strategy_options)
        value, time, measure_unit = merger.merge(
            self.output, sensor_data, self.inputs.all())
        if value:
            self.output.push_data(value=value, time=time,
                                  measure_unit=measure_unit)


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
        choices=(
            ('iot.actuators.actuator.NullActuator', _('Null Actuator')),
            ('iot.actuators.parport.DataPin', _('Parallel Port Pin')),
            ('iot.actuators.firmata.FirmataPin', _(
                'Arduino Pin using Firmata Protocol')),
            ('iot.actuators.mqtt.MqttDevice', _('Mqtt Remote Device')),
        ),
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
            try:
                return device.get_value()
            except NotImplementedError:
                pass
        data = self.data.all().order_by('-time').first()
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
        ordering = ('-time',)

    time = models.DateTimeField(
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
