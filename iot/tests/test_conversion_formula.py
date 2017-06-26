from decimal import Decimal

from django.test import TestCase
from iot.models import ConversionFormula


class ConversionFormulaTest(TestCase):
    def test_to_decimal(self):
        expected = 'Decimal(\'1\') + Decimal(\'1\')'
        result = ConversionFormula(formula='1 + 1').prepare_formula()
        self.assertEqual(expected, result)


class TemperatureTest(TestCase):
    # kelvin celsius fahrenheit
    temperatures = (
        (Decimal('0.0'), Decimal('-273.15'), Decimal('-459.67'),),
        (Decimal('77.35'), Decimal('-195.8'), Decimal('-320.44'),),
        (Decimal('195.15'), Decimal('-78.0'), Decimal('-108.4'),),
        (Decimal('233.15'), Decimal('-40.0'), Decimal('-40.0'),),
        (Decimal('273.1499'), Decimal('-0.0001'), Decimal('31.9998'),),
        (Decimal('273.16'), Decimal('0.01'), Decimal('32.018'),),
        (Decimal('310.15'), Decimal('37.0'), Decimal('98.6'),),
        (Decimal('373.1339'), Decimal('99.9839'), Decimal('211.971'),),
    )

    def test_c_to_f(self):
        formula = ConversionFormula.objects.get(
            from_unit__name='celsius',
            to_unit__name='fahrenheit',
        )
        for k, c, f in self.temperatures:
            converted = formula.convert_fast(c)
            self.assertAlmostEqual(float(f), converted, delta=0.1)
            converted = formula.convert_precisely(c)
            self.assertAlmostEqual(f, converted, delta=Decimal('0.0001'))

    def test_c_to_k(self):
        formula = ConversionFormula.objects.get(
            from_unit__name='celsius',
            to_unit__name='kelvin',
        )
        for k, c, f in self.temperatures:
            converted = formula.convert_fast(c)
            self.assertAlmostEqual(float(k), converted, delta=0.1)
            converted = formula.convert_precisely(c)
            self.assertAlmostEqual(k, converted, delta=Decimal('0.0001'))

    def test_f_to_c(self):
        formula = ConversionFormula.objects.get(
            from_unit__name='fahrenheit',
            to_unit__name='celsius',
        )
        for k, c, f in self.temperatures:
            converted = formula.convert_fast(f)
            self.assertAlmostEqual(float(c), converted, delta=0.1)
            converted = formula.convert_precisely(f)
            self.assertAlmostEqual(c, converted, delta=Decimal('0.0001'))

    def test_f_to_k(self):
        formula = ConversionFormula.objects.get(
            from_unit__name='fahrenheit',
            to_unit__name='kelvin',
        )
        for k, c, f in self.temperatures:
            converted = formula.convert_fast(f)
            self.assertAlmostEqual(float(k), converted, delta=0.1)
            converted = formula.convert_precisely(f)
            self.assertAlmostEqual(k, converted, delta=Decimal('0.0001'))

    def test_k_to_c(self):
        formula = ConversionFormula.objects.get(
            from_unit__name='kelvin',
            to_unit__name='celsius',
        )
        for k, c, f in self.temperatures:
            converted = formula.convert_fast(k)
            self.assertAlmostEqual(float(c), converted, delta=0.1)
            converted = formula.convert_precisely(k)
            self.assertAlmostEqual(c, converted, delta=Decimal('0.0001'))

    def test_k_to_f(self):
        formula = ConversionFormula.objects.get(
            from_unit__name='kelvin',
            to_unit__name='fahrenheit',
        )
        for k, c, f in self.temperatures:
            converted = formula.convert_fast(k)
            self.assertAlmostEqual(float(f), converted, delta=0.1)
            converted = formula.convert_precisely(k)
            self.assertAlmostEqual(f, converted, delta=Decimal('0.0001'))
