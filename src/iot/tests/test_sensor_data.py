from channels.tests import ChannelTestCase as TestCase
from iot.models import Sensor, SensorData, Position, MeasureUnit
from model_mommy import mommy


class TestSensor(TestCase):
    def test_init_data(self):
        position = mommy.make(Position)
        celsius = MeasureUnit.objects.select_related('magnitude').get(name='celsius')
        sensor = mommy.make(
            Sensor,
            position=position,
            measure_unit=celsius,
            magnitude=celsius.magnitude
        )
        for x in range(0, 10):
            sensor.push_data(value=x)
        data = SensorData.objects.all()
        self.assertEqual(10, data.count())
        for sample in data:
            self.assertEqual(position, sample.position)
            self.assertEqual(celsius, sample.measure_unit)
