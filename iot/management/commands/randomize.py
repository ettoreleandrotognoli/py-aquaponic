import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from iot.models import Sensor, Magnitude, MeasureUnit


class Command(BaseCommand):
    help = 'Randomize data of a sensor'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sensor-name',
            dest='sensor_name',
            help='Sensor name'
        )

        parser.add_argument(
            '--magnitude',
            dest='magnitude_name',
            help='Magnitude name',
            default='temperature'
        )

        parser.add_argument(
            '--unit',
            dest='unit_name',
            help='Unit name',
            default='celsius',
        )

        parser.add_argument(
            '--limit',
            dest='limit',
            help='Sample size',
            default=100,
            type=int,
        )

        parser.add_argument(
            '--min',
            dest='min_value',
            default=-50,
            help='Min value',
            type=float
        )

        parser.add_argument(
            '--max',
            dest='max_value',
            default=50,
            help='Max value',
            type=float
        )

        parser.add_argument(
            '--interval',
            dest='interval',
            default=5,
            help='Time interval in seconds'
        )

        parser.add_argument(
            '--low-pass',
            dest='low_pass',
            default=0,
            help='Low pass filter',
            type=float
        )

    def _handle(self, sensor_name, magnitude_name, unit_name, min_value, max_value, limit, interval, low_pass,
                **kwargs):
        magnitude = Magnitude.objects.get(name=magnitude_name)
        unit = MeasureUnit.objects.get(name=unit_name)
        defaults = {'measure_unit': unit, 'magnitude': magnitude}
        sensor, created = Sensor.objects.get_or_create(name=sensor_name, defaults=defaults)
        if created:
            self.stdout.write(self.style.SUCCESS('Sensor %s created' % sensor_name))
        time = timezone.now() - timezone.timedelta(seconds=interval * limit)
        value = random.uniform(min_value, max_value)
        for x in range(limit):
            new_value = random.uniform(min_value, max_value)
            value = (value * low_pass + new_value) / (low_pass + 1)
            sensor.push_data(time=time, value=value)
            time += timezone.timedelta(seconds=interval)

    def handle(self, *args, **options):
        self._handle(**options)
        self.stdout.write(self.style.SUCCESS('Successfully'))
