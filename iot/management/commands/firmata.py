import threading
import time

from channels import DEFAULT_CHANNEL_LAYER, channel_layers
from channels.routing import route
from channels.worker import Worker
from django.core.management import BaseCommand, CommandError
from pyfirmata import Arduino, util, PWM

from iot.models import Actuator
from iot.models import Sensor, Magnitude, MeasureUnit

electric_tension = Magnitude.objects.get(name='electric tension')
volt = MeasureUnit.objects.get(name='volt')
proportion = Magnitude.objects.get(name='proportion')
percentage = MeasureUnit.objects.get(name='percentage')


class Command(BaseCommand):
    help = 'Read pins of arduino using firmata protocol'
    channel_layer = None

    def add_arguments(self, parser):
        parser.add_argument(
            '--device',
            dest='device',
            help='Arduino TTY',
            type=str,
        )
        parser.add_argument(
            '--interval',
            dest='interval',
            default=1.0,
            type=float,
        )
        parser.add_argument(
            '--name-prefix',
            dest='name_prefix',
            default='arduino',
            type=str,
        )
        parser.add_argument(
            '--v-ref',
            dest='vref',
            default=5.0,
            type=float,
        )

    def _handle(self, device, interval, name_prefix, vref, **kwargs):

        try:
            board = Arduino(device)
        except Exception as ex:
            self.stdout.write(self.style.ERROR('Arduino with firmata not detected'))
            self.stdout.write(self.style.ERROR(ex))
            return
        it = util.Iterator(board)
        it.start()
        for analog_pin in board.analog:
            analog_pin.enable_reporting()
            pin = 'a%d' % analog_pin.pin_number
            sensor_name = '%s-%s' % (name_prefix, pin)
            sensor, created = Sensor.objects.get_or_create(name=sensor_name, defaults=dict(
                magnitude=electric_tension,
                measure_unit=volt
            ))
            if created:
                self.stdout.write(self.style.SUCCESS('Sensor "%s" created!' % sensor_name))

        for digital_pin in board.digital:
            pin = 'd%d' % digital_pin.pin_number
            actuator_name = '%s-%s' % (name_prefix, pin)
            actuator, created = Actuator.objects.get_or_create(name=actuator_name, defaults=dict(
                magnitude=proportion,
                measure_unit=percentage,
                strategy='iot.actuators.firmata.FirmataPin',
                strategy_options=dict(pin=digital_pin.pin_number),
            ))
            try:
                digital_pin.mode = PWM
            except:
                pass
            if created:
                self.stdout.write(self.style.SUCCESS('Actuator "%s" created!' % actuator_name))

        def set_pin(pin, value):
            if board.digital[pin].mode == PWM:
                board.digital[pin].write(value)
            else:
                board.digital[pin].write(round(value))

        def firmata_consumer(message, **kwargs):
            set_pin(**message.content)

        self.channel_layer.router.add_route(route('firmata', firmata_consumer))

        worker = WorkerThread(self.channel_layer)
        worker.daemon = True
        worker.start()

        while True:
            time.sleep(interval)
            for analog_pin in board.analog:
                pin = 'a%d' % analog_pin.pin_number
                sensor_name = '%s-%s' % (name_prefix, pin)
                sensor = Sensor.objects.get(name=sensor_name)
                raw_value = analog_pin.read()
                sensor.push_data(
                    value=raw_value * vref,
                    raw=raw_value
                )

    def handle(self, *args, **options):
        self.channel_layer = channel_layers[options.get("layer", DEFAULT_CHANNEL_LAYER)]
        if self.channel_layer.local_only():
            raise CommandError(
                "You cannot span multiple processes with the in-memory layer. " +
                "Change your settings to use a cross-process channel layer."
            )

        self._handle(**options)


class WorkerThread(threading.Thread):
    """
    Class that runs a worker
    """

    def __init__(self, channel_layer):
        super(WorkerThread, self).__init__()
        self.channel_layer = channel_layer

    def run(self):
        worker = Worker(channel_layer=self.channel_layer, signal_handlers=False)
        worker.ready()
        worker.run()
