from pydoc import locate
from django.db import models
from django.db.models.manager import BaseManager
from jsonfield import JSONField
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from paho.mqtt.client import Client as MqttClient

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

    def config(self, mqtt_client: MqttClient):
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

    def mqtt_on_connect(self, mqtt_client: MqttClient, userdata, flag, rc):
        mqtt_client.subscribe(self.subscribe_topic, self.qos)

    def mqtt_on_message(self, mqtt_client: MqttClient, userdata, msg):
        strategy = self.load_strategy()
        for sensor_data in strategy.parse(mqtt_client, userdata, msg):
            sensor_data.save()

    def make_client(self) -> MqttClient:
        mqtt_client = MqttClient()
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
                channel_layer.router.add_route(
                    route(self.channel, self.consumer))
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
