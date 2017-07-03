import time
from pyfirmata import Arduino, util
from django.core.management.base import BaseCommand

from iot.models import Sensor, Magnitude, MeasureUnit


class Command(BaseCommand):
    help = 'Read pins of arduino using firmata protocol'

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
        electric_tension = Magnitude.objects.get(name='electric tension')
        volt = MeasureUnit.objects.get(name='volt')
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
        self._handle(**options)
