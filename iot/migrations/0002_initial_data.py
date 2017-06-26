# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-26 14:09
from __future__ import unicode_literals

from django.db import migrations


def forwards_func(apps, schema_editor):
    Magnitude = apps.get_model('iot', 'Magnitude')
    db_alias = schema_editor.connection.alias
    Magnitude.objects.using(db_alias).bulk_create([
        Magnitude(name='temperature', description=''),
        Magnitude(name='mass', description=''),
        Magnitude(name='distance', description=''),
        Magnitude(name='time', description=''),
        Magnitude(name='speed', description=''),
        Magnitude(name='angular speed', description=''),
        Magnitude(name='acidity', description=''),
        Magnitude(name='electric tension', description=''),
        Magnitude(name='electric resistance', description=''),
        Magnitude(name='electric current', description=''),
        Magnitude(name='frequency', description=''),
        Magnitude(name='light', description=''),
    ])

    MeasureUnit = apps.get_model('iot', 'MeasureUnit')

    temperature = Magnitude.objects.using(db_alias).get(name='temperature')
    MeasureUnit.objects.using(db_alias).bulk_create([
        MeasureUnit(name='celsius', symbol='°C', magnitude=temperature),
        MeasureUnit(name='fahrenheit', symbol='°F', magnitude=temperature),
        MeasureUnit(name='kelvin', symbol='K', magnitude=temperature),
    ])

    mass = Magnitude.objects.using(db_alias).get(name='mass')
    MeasureUnit.objects.using(db_alias).bulk_create([
        MeasureUnit(name='gramme', symbol='g', magnitude=mass),
    ])

    distance = Magnitude.objects.using(db_alias).get(name='distance')
    MeasureUnit.objects.using(db_alias).bulk_create([
        MeasureUnit(name='metre', symbol='m', magnitude=distance),
        MeasureUnit(name='inch', symbol='"', magnitude=distance),
        MeasureUnit(name='yard', symbol='yd', magnitude=distance),
        MeasureUnit(name='foot', symbol='\'', magnitude=distance),
    ])

    time = Magnitude.objects.using(db_alias).get(name='time')
    MeasureUnit.objects.using(db_alias).bulk_create([
        MeasureUnit(name='second', symbol='s', magnitude=time),
        MeasureUnit(name='hour', symbol='h', magnitude=time),
        MeasureUnit(name='minute', symbol='m', magnitude=time),
    ])

    speed = Magnitude.objects.using(db_alias).get(name='speed')
    MeasureUnit.objects.using(db_alias).bulk_create([
        MeasureUnit(name='metre per second', symbol='m/s', magnitude=speed)
    ])

    acidity = Magnitude.objects.using(db_alias).get(name='acidity')
    MeasureUnit.objects.using(db_alias).bulk_create([
        MeasureUnit(name='potential of hydrogen', symbol='pH', magnitude=acidity)
    ])

    electric_tension = Magnitude.objects.get(name='electric tension')
    MeasureUnit.objects.using(db_alias).bulk_create([
        MeasureUnit(name='volts', symbol='V', magnitude=electric_tension)
    ])

    electric_resistance = Magnitude.objects.get(name='electric resistance')
    MeasureUnit.objects.using(db_alias).bulk_create([
        MeasureUnit(name='ohm', symbol='Ω', magnitude=electric_resistance)
    ])

    electric_current = Magnitude.objects.get(name='electric current')
    MeasureUnit.objects.using(db_alias).bulk_create([
        MeasureUnit(name='amper', symbol='A', magnitude=electric_current)
    ])

    frequency = Magnitude.objects.get(name='frequency')
    MeasureUnit.objects.using(db_alias).bulk_create([
        MeasureUnit(name='hertz', symbol='Hz', magnitude=frequency)
    ])

    light = Magnitude.objects.using(db_alias).get(name='light')
    MeasureUnit.objects.using(db_alias).bulk_create([
        MeasureUnit(name='luminous flux', symbol='lm', magnitude=light)
    ])

    ConversionFormula = apps.get_model('iot', 'ConversionFormula')

    celsius = MeasureUnit.objects.using(db_alias).get(name='celsius')
    fahrenheit = MeasureUnit.objects.using(db_alias).get(name='fahrenheit')
    kelvin = MeasureUnit.objects.using(db_alias).get(name='kelvin')
    ConversionFormula.objects.using(db_alias).bulk_create([
        ConversionFormula(from_unit=celsius, to_unit=kelvin, formula='%f + 273.15'),
        ConversionFormula(from_unit=celsius, to_unit=fahrenheit, formula='%f * 1.8 + 32'),
        ConversionFormula(from_unit=fahrenheit, to_unit=celsius, formula='(%f - 32) / 1.8'),
        ConversionFormula(from_unit=fahrenheit, to_unit=kelvin, formula='(%f + 459.67) / 1.8'),
        ConversionFormula(from_unit=kelvin, to_unit=celsius, formula='%f - 273.15'),
        ConversionFormula(from_unit=kelvin, to_unit=fahrenheit, formula='%f * 1.8 - 459.67'),
    ])


def reverse_func(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Magnitude = apps.get_model('iot', 'Magnitude')
    Magnitude.objects.using(db_alias).all().delete()
    MeasureUnit = apps.get_model('iot', 'MeasureUnit')
    MeasureUnit.objects.using(db_alias).all().delete()
    ConversionFormula = apps.get_model('iot', 'ConversionFormula')
    ConversionFormula.objects.using(db_alias).all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('iot', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func)
    ]
