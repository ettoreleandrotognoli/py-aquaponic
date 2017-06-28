import parallel
from iot.models import Actuator
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Randomize data of a sensor'

    def _handle(self, **kwargs):

        pass

    def _parallel(self, **kwargs):
        try:
            self.parallel = parallel.Parallel()
        except Exception as ex:
            self.stdout.write(self.style.ERROR('Parallel port not detected'))
            self.stdout.write(self.style.ERROR(str(ex)))
            return
        for pin in range(8):
            Actuator.objects.get_or_create(name='parport-d%d' % pin, defaults={
                'strategy': 'iot.parport.DataPin',
                'strategy_options': {'pin': pin}
            })
        self.stdout.write(self.style.SUCCESS('Parallel port detected successfully'))

    def handle(self, *args, **options):
        self._parallel(**options)
