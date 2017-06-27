from django.contrib import admin
from iot import models


@admin.register(models.Magnitude)
class MagnitudeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.MeasureUnit)
class MeasureUnitAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ['name', 'endpoint', 'magnitude', 'measure_unit', ]
    list_filter = ['magnitude', 'measure_unit', ]
    search_fields = ['name', 'endpoint']


@admin.register(models.SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ['time', 'value', 'sensor', 'measure_unit']
    list_filter = ['sensor', 'measure_unit', ]


@admin.register(models.Position)
class PositionAdmin(admin.ModelAdmin):
    pass


@admin.register(models.ConversionFormula)
class ConversionFormulaAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'formula', 'from_unit', 'to_unit']
    list_filter = ['from_unit', 'to_unit']
    search_fields = [
        'formula',
        'from_unit__symbol',
        'from_unit__name',
        'to_unit__symbol',
        'from_unit__name',
    ]


@admin.register(models.Actuator)
class ActuatorAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'endpoint']
    search_fields = [
        'name',
        'description',
        'endpoint',
    ]


@admin.register(models.PID)
class PIDAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'active', 'input', 'output', 'kp', 'ki', 'kd']
    list_filter = ['active', 'input__magnitude']
    search_fields = [
        'input__name',
        'output__name',
    ]


@admin.register(models.SensorFusion)
class SensorFusionAdmin(admin.ModelAdmin):
    list_display = ['output', 'fusion_strategy']
    list_filter = [
        'output__magnitude',
        'fusion_strategy',
    ]
    search_fields = [
        'inputs__name',
        'output__name',
    ]
