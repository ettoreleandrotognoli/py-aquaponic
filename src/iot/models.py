<<<<<<< HEAD
=======
from decimal import Decimal
from pydoc import locate

>>>>>>> 6101720d5b73be9a3257384bf71dee7668701676
import re
from decimal import Decimal
from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone
from django.utils.timezone import datetime
from django.utils.timezone import timedelta
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from functools import reduce
from jsonfield import JSONField
from paho.mqtt import client as mqtt
from pydoc import locate
from uuid import uuid4 as unique

from core.utils.models import ValidateOnSaveMixin


def generic_consumer(message):
    model = apps.get_model(message.content['model'])
    instance = model.objects.get(pk=message.content['pk'])
    method = getattr(instance, message.content['method'])
    method(*message.content['args'], **message.content['kwargs'])


class MQTTConnection(models.Model):
    class Meta:
        verbose_name = _('MQTT Broker Connection')

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('Name'),
    )

    host = models.CharField(
        max_length=255,
        verbose_name=_('Host'),
        default='iot.eclipse.org',
    )

    port = models.IntegerField(
        default=1883,
        verbose_name=_('Port'),
    )

    username = models.CharField(
        blank=True,
        null=True,
        max_length=255,
    )

    password = models.CharField(
        blank=True,
        null=True,
        max_length=255,
    )

    def __str__(self):
        return self.name

    def config(self, mqtt_client: mqtt.Client):
        if self.username and self.password:
            mqtt_client.username_pw_set(self.username, self.password)
        mqtt_client.connect(
            self.host,
            self.port,
        )


class MQTTDataSource(models.Model):
    class Meta:
        verbose_name = _('MQTT Data Source')

    mqtt_client = None

    active = models.BooleanField(
        default=True,
    )

    running = models.BooleanField(
        default=False,
    )

    connection = models.ForeignKey(
        'MQTTConnection',
        on_delete=models.CASCADE,
    )

    subscribe_topic = models.CharField(
        max_length=255,
        default='py-aquaponic/#'
    )

    qos = models.IntegerField(
        choices=(
            (0, '0'),
            (1, '1'),
            (2, '2'),
        ),
        default=0,
    )

    strategy = models.CharField(
        max_length=255,
        verbose_name=_('Parse Strategy'),
        choices=(
            ('iot.data_source.mqtt.MQTTSingleTopicSensor', _('Single Sensor Topic')),
        )
    )

    strategy_options = JSONField(
        blank=True,
        null=True,
    )

    def load_strategy(self):
        strategy_class = locate(self.strategy)
        strategy_instance = strategy_class(**self.strategy_options)
        return strategy_instance

    def mqtt_on_connect(self, mqtt_client: mqtt.Client, userdata, flag, rc):
        mqtt_client.subscribe(self.subscribe_topic, self.qos)

    def mqtt_on_message(self, mqtt_client: mqtt.Client, userdata, msg):
        strategy = self.load_strategy()
        for sensor_data in strategy.parse(mqtt_client, userdata, msg):
            sensor_data.save()

    def make_client(self) -> mqtt.Client:
        mqtt_client = mqtt.Client()
        mqtt_client.on_connect = self.mqtt_on_connect
        mqtt_client.on_message = self.mqtt_on_message
        self.connection.config(mqtt_client)
        return mqtt_client

    def get_channel(self):
        return 'mqtt_data_source_%d' % self.pk

    channel = property(get_channel)

    def consumer(self, message):
        method = getattr(self, message.content['method'])
        method(*message.content['args'], **message.content['kwargs'])

    def _acquire(self):
        rows_affected = MQTTDataSource.objects.filter(
            pk=self.pk,
            running=False,
        ).update(
            running=True
        )
        return rows_affected

    def _release(self):
        rows_affected = MQTTDataSource.objects.filter(
            pk=self.pk,
            running=True,
        ).update(
            running=False
        )
        return rows_affected

    def start(self):
        rows_affected = self._acquire()
        if rows_affected == 0:
            return
        if rows_affected != 1:
            raise Exception()
        try:
            from channels.asgi import channel_layers
            from channels import route
            from channels import DEFAULT_CHANNEL_LAYER
            channel_layer = channel_layers[DEFAULT_CHANNEL_LAYER]
            if self.mqtt_client is None:
                channel_layer.router.add_route(route(self.channel, self.consumer))
            self.mqtt_client = self.make_client()
            self.mqtt_client.loop_start()
        except:
            self._release()

    def restart(self):
        self.stop()
        self.start()

    def stop(self):
        rows_affected = self._release()
        if rows_affected == 0:
            return
        if rows_affected != 1:
            raise Exception()
        self.mqtt_client.loop_stop()

    def send_update(self):
        from channels import Channel
        if not self.active:
            if self.running:
                self.send_stop()
            return
        if self.running:
            Channel(self.channel).send(dict(
                method='restart',
                args=(),
                kwargs={}
            ))
        else:
            self.send_start()

    def send_start(self):
        from channels import Channel
        Channel('iot.mqtt_data_source').send(dict(
            model='iot.MQTTDataSource',
            pk=self.pk,
            method='start',
            args=(),
            kwargs={}
        ))

    def send_stop(self):
        from channels import Channel
        Channel(self.channel).send(
            method='stop',
            args=(),
            kwargs={}
        )


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
        unique_together =(
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
            ('from_unit','to_unit',),
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


class PositionQuerySet(models.QuerySet):
    pass

class PositionManager(BaseManager.from_queryset(PositionQuerySet)):
    pass

class Position(models.Model):

    objects = PositionManager()

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

class SensorDataQuerySet(models.QuerySet):
    pass

class SensorDataManager(BaseManager.from_queryset(SensorDataQuerySet)):
    pass

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
        on_delete=models.CASCADE,
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
            error_message = ugettext('measure unit magnitude and sensor magnitude are different')
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
        on_delete=models.CASCADE,
    )

    position = models.OneToOneField(
        'Position',
        related_name='sensor',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
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


class SensorFusionQuerySet(models.QuerySet):
    pass

class SensorFusionManager(BaseManager.from_queryset(SensorDataQuerySet)):
    pass

class SensorFusion(models.Model):

    objects =SensorFusionManager()

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
        on_delete=models.CASCADE,
    )

    strategy = models.CharField(
        max_length=255,
        verbose_name=_('Fusion strategy'),
        choices=(
            ('iot.fusion.sampling.HighSampling', _('High Sampling')),
            ('iot.fusion.ldr.Lumen', _('Electric Tension to Lumen using a LDR')),
            ('iot.fusion.ldr.Lux', _('Electric Tension to Lux using a LDR')),
            ('iot.fusion.thermistor.SteinhartHart', _('Temperatude with Steinhart-Hart (NTC Thermistor) ')),
            ('iot.fusion.thermistor.BetaFactor', _('Temperatude with Beta Factor (NTC Thermistor) ')),
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
        value, time, measure_unit = merger.merge(self.output, sensor_data, self.inputs.all())
        if value:
            self.output.push_data(value=value, time=time, measure_unit=measure_unit)

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
        on_delete=models.CASCADE,
    )

    strategy = models.CharField(
        max_length=255,
        choices=(
            ('iot.actuators.actuator.NullActuator', _('Null Actuator')),
            ('iot.actuators.parport.DataPin', _('Parallel Port Pin')),
            ('iot.actuators.firmata.FirmataPin', _('Arduino Pin using Firmata Protocol')),
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
        on_delete=models.CASCADE,
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
        on_delete=models.CASCADE,
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
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return '%s (%f)' % (self.actuator.name, self.value)


class PID(models.Model):
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
<<<<<<< HEAD
        on_delete=models.CASCADE,
        related_name='pid_controllers'
=======
        related_name='pid_controllers',
        on_delete=models.CASCADE,
>>>>>>> 6101720d5b73be9a3257384bf71dee7668701676
    )

    output = models.ForeignKey(
        Actuator,
<<<<<<< HEAD
        on_delete=models.CASCADE,
        related_name='pid_controllers'
=======
        related_name='pid_controllers',
        on_delete=models.CASCADE,
>>>>>>> 6101720d5b73be9a3257384bf71dee7668701676
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
        last = self.input.data.exclude(pk=sensor_data.pk).order_by('-time').first()
        interval = sensor_data.time - last.time if last else timedelta(seconds=0)
        self.update(sensor_data.value, interval)

    def __str__(self):
        return self.name


class TriggerCondition(ValidateOnSaveMixin, models.Model):
    input = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
    )

    params = JSONField(

    )

    check_script = models.CharField(
        max_length=255,
        choices=(
            ('s > p', _('>')),
            ('s >= p', _('>=')),
            ('s < p', _('<')),
            ('s <= p', _('<=')),
            ('s == p', _('=')),
            ('s != p', _('!=')),
            ('s >= p0 and s <= p1', _('between')),
        )
    )

    trigger = models.ForeignKey(
        'Trigger',
        on_delete=models.CASCADE,
        related_name='conditions',
        on_delete=models.CASCADE,
    )

    def clean(self):
        try:
            self.check_condition(0.0)
        except Exception as ex:
            raise ValidationError({
                'params': ex.message,
                'check_script': ex.message,
            })

    def check_condition(self, sensor_value=None):
        if sensor_value is None:
            sensor_value = self.input.value
        params = self.params
        if isinstance(params, dict):
            params = params
        elif isinstance(params, list):
            params = dict([('p%d' % k, v) for k, v in zip(range(len(params)), params)])
        else:
            params = dict(p=params)
        params.update(dict(s=sensor_value))
        return eval(self.check_script, {}, params)


class TriggerAction(models.Model):
    output_type_queryset = models.Q(app_label='iot', model='pid') | models.Q(app_label='iot', model='actuator')

    output_value = models.FloatField(

    )

    output_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=output_type_queryset,
    )

    output_pk = models.PositiveIntegerField(

    )

    output = GenericForeignKey('output_type', 'output_pk')

    trigger = models.ForeignKey(
        'Trigger',
        on_delete=models.CASCADE,
        related_name='actions',
        on_delete=models.CASCADE,
    )

    def do_action(self):
        self.output.value = self.output_value


class TriggerQuerySet(models.QuerySet):
    pass

class TriggerManager(BaseManager.from_queryset(TriggerQuerySet)):
    pass

class Trigger(models.Model):

    objects = TriggerManager()

    active = models.BooleanField(
        default=True,
    )

    name = models.CharField(
        max_length=255,
        unique=True,
    )

    reduce_operator = models.CharField(
        max_length=255,
        choices=(
            ('operator.and_', _('And')),
            ('operator.or_', _('Or')),
        )
    )

    def check_conditions(self):
        results = [condition.check_condition() for condition in self.conditions.all()]
        return reduce(locate(self.reduce_operator), results)

    def try_fire(self):
        if not self.check_conditions():
            return
        for action in self.actions.all():
            action.do_action()
