import json

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from paho.mqtt import client as mqtt

from iot.models import Sensor


def build_collector(collect_key: str):
    keys = collect_key.split('.')

    def collector(data: dict):
        for k in keys:
            if not data:
                return data
            data = data.get(k, None)
        return data

    return collector


class Command(BaseCommand):
    help = 'Start a daemon to listening a mqtt broker'

    def add_arguments(self, parser):
        parser.add_argument(
            '--topic',
            dest='topic',
            help='Mqtt Topic',
            default='$SYS/py-aquaponic/#',
        )

        parser.add_argument(
            '--port',
            dest='port',
            help='Mqtt service port',
            type=int,
            default=1883
        )

        parser.add_argument(
            '--host',
            dest='host',
            help='Mqtt broker address',
            default='iot.eclipse.org'
        )

        parser.add_argument(
            '--user-name',
            dest='user_name',
        )

        parser.add_argument(
            '--user-pass',
            dest='user_pass',
        )

        parser.add_argument(
            '--collect-key',
            dest='collect_key',
        )

    def _handle(self, host, port, topic, user_name, user_pass, collect_key, **kwargs):

        if collect_key:
            collector = build_collector(collect_key)
        else:
            collector = lambda x: x

        def on_connect(mqtt_client: mqtt.Client, userdata, flag, rc):
            mqtt_client.subscribe(topic)

        def on_message(mqtt_client: mqtt.Client, userdata, msg):
            self.stdout.write(self.style.SUCCESS('Data received from %s: %s' % tuple(map(str, (
                msg.topic,
                msg.payload,
            )))))
            final_topic = msg.topic.split('/')[-1]
            try:
                sensor = Sensor.objects.get(endpoint=final_topic)
            except ObjectDoesNotExist as ex:
                self.stdout.write(self.style.ERROR(ex))
                return

            try:
                data = json.loads(msg.payload.decode('utf-8'))
            except Exception as ex:
                self.stdout.write(self.style.ERROR(ex))
                return

            data = collector(data)
            if not isinstance(data, dict):
                data = dict(value=float(data))
            sensor.push_data(**data)

        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        if user_name or user_pass:
            client.username_pw_set(user_name, user_pass)
        self.stdout.write(self.style.SUCCESS('Connecting...'))
        client.connect(
            host=host,
            port=port,
        )
        self.stdout.write(self.style.SUCCESS('Listening...'))
        client.loop_forever()

    def handle(self, *args, **options):
        self._handle(**options)
