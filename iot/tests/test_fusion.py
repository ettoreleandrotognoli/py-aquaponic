from django.test import TestCase

from iot.fusion.electronic import VoltageDivider
from iot.fusion.thermistor import SteinhartHart
from iot.fusion.thermistor import BetaFactor
from iot.models import SensorData, MeasureUnit

volt = MeasureUnit.objects.get(name='volt')


class TestVoltageDivider(TestCase):
    def test_half(self):
        voltage_divider = VoltageDivider(
            r1=10000,
            r2=10000,
            vi=5,
        )
        result = voltage_divider.calc_vo()
        self.assertAlmostEqual(2.5, result, delta=0.001)


class TestSteinhartHart(TestCase):
    def test_ntc_10k(self):
        tension = 5
        thermistor = 10000.0
        resistor = 10000.0
        voltage_divider = VoltageDivider(
            r1=resistor,
            r2=thermistor,
            vi=tension,
        )
        vo = voltage_divider.calc_vo()

        steinhart_hart = SteinhartHart(
            resistor=resistor,
            tension=tension,
            proportional=True,
            output='celsius',
            a=0.0011303,
            b=0.0002339,
            c=0.00000008863,
        )
        result, time, unit = steinhart_hart.merge(SensorData(
            value=vo,
            measure_unit=volt,
        ), [])
        self.assertEqual(unit.name, 'celsius')
        self.assertAlmostEqual(25, result, delta=0.1)


class TestBetaFactor(TestCase):
    def test_ntc_10k_3950(self):
        tension = 5
        thermistor = 10000.0
        resistor = 10000.0
        voltage_divider = VoltageDivider(
            r1=resistor,
            r2=thermistor,
            vi=tension,
        )
        vo = voltage_divider.calc_vo()

        beta_factor = BetaFactor(
            resistor=resistor,
            tension=tension,
            proportional=True,
            output='celsius',
            b=3950.0,
            r=thermistor,
            t=298.15,
        )
        result, time, unit = beta_factor.merge(SensorData(
            value=vo,
            measure_unit=volt,
        ), [])
        self.assertEqual(unit.name, 'celsius')
        self.assertAlmostEqual(25, result, delta=0.1)