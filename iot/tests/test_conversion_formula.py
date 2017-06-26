from decimal import Decimal

from django.test import TestCase
from iot.models import ConversionFormula


class ConversionFormulaTest(TestCase):
    def test_to_decimal(self):
        expected = 'Decimal(1) + Decimal(1)'
        result = ConversionFormula(formula='1 + 1').prepared_formula
        self.assertEqual(expected, result)


class TemperatureTest(TestCase):
    # kelvin celsius fahrenheit
    temperatures = (
        (Decimal(0.0), -273.15, -459.67,),
        (Decimal(77.4), -195.8, -320.4,),
        (Decimal(195.1), -78.0, -108.4,),
        (Decimal(233.15), -40.0, -40.0,),
        (Decimal(273.1499), -0.0001, 31.9998,),
        (Decimal(273.16), 0.01, 32.018,),
        (Decimal(310.15), 37.0, 98.6,),
        (Decimal(373.1339), 99.9839, 211.971,),
    )

    def test_c_to_f(self):
        formula = ConversionFormula.objects.get(
            from_unit__name='celsius',
            to_unit__name='fahrenheit',
        )
        for k, c, f in self.temperatures:
            converted = formula.convert_fast(c)
            self.assertAlmostEqual(f, converted, delta=0.1)
            converted = formula.convert_precisely(c)
            self.assertAlmostEqual(Decimal(f), converted, delta=0.0001)

    def test_c_to_k(self):
        formula = ConversionFormula.objects.get(
            from_unit__name='celsius',
            to_unit__name='kelvin',
        )
        for k, c, f in self.temperatures:
            converted = formula.convert_fast(c)
            self.assertAlmostEqual(k, converted, delta=0.1)

    def test_f_to_c(self):
        formula = ConversionFormula.objects.get(
            from_unit__name='fahrenheit',
            to_unit__name='celsius',
        )
        for k, c, f in self.temperatures:
            converted = formula.convert_fast(f)
            self.assertAlmostEqual(c, converted, delta=0.1)

    def test_f_to_k(self):
        formula = ConversionFormula.objects.get(
            from_unit__name='fahrenheit',
            to_unit__name='kelvin',
        )
        for k, c, f in self.temperatures:
            converted = formula.convert_fast(f)
            self.assertAlmostEqual(k, converted, delta=0.1)

    def test_k_to_c(self):
        formula = ConversionFormula.objects.get(
            from_unit__name='kelvin',
            to_unit__name='celsius',
        )
        for k, c, f in self.temperatures:
            converted = formula.convert_fast(k)
            self.assertAlmostEqual(c, converted, delta=0.1)

    def test_k_to_f(self):
        formula = ConversionFormula.objects.get(
            from_unit__name='kelvin',
            to_unit__name='fahrenheit',
        )
        for k, c, f in self.temperatures:
            converted = formula.convert_fast(k)
            self.assertAlmostEqual(f, converted, delta=0.1)
