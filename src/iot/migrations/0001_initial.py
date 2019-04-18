# Generated by Django 2.2 on 2019-04-18 20:09

import core.utils.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Actuator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('strategy', models.CharField(choices=[('iot.actuators.actuator.NullActuator', 'Null Actuator'), ('iot.actuators.parport.DataPin', 'Parallel Port Pin'), ('iot.actuators.firmata.FirmataPin', 'Arduino Pin using Firmata Protocol'), ('iot.actuators.mqtt.MqttDevice', 'Mqtt Remote Device')], max_length=255)),
                ('strategy_options', jsonfield.fields.JSONField(blank=True, default={}, null=True)),
            ],
            options={
                'verbose_name': 'Actuator',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Magnitude',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
            ],
            options={
                'verbose_name': 'Magnitude',
                'ordering': ('name',),
                'unique_together': {('name',)},
            },
        ),
        migrations.CreateModel(
            name='MeasureUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=8, verbose_name='Symbol')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('magnitude', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='measures_units', to='iot.Magnitude')),
            ],
            options={
                'verbose_name': 'Measure Unit',
                'ordering': ('name',),
                'unique_together': {('name',)},
            },
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField(verbose_name='Latitude')),
                ('longitude', models.FloatField(verbose_name='Longitude')),
                ('altitude', models.FloatField(verbose_name='Altitude')),
            ],
            options={
                'verbose_name': 'Position',
            },
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('is_virtual', models.BooleanField(default=False, verbose_name='It is a virtual sensor')),
                ('magnitude', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sensors', to='iot.Magnitude')),
                ('measure_unit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sensors', to='iot.MeasureUnit')),
                ('position', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sensor', to='iot.Position')),
            ],
            options={
                'verbose_name': 'Sensor',
                'ordering': ('name',),
            },
            bases=(core.utils.models.ValidateOnSaveMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Trigger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('reduce_operator', models.CharField(choices=[('operator.and_', 'And'), ('operator.or_', 'Or')], max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='TriggerCondition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('params', jsonfield.fields.JSONField()),
                ('check_script', models.CharField(choices=[('s > p', '>'), ('s >= p', '>='), ('s < p', '<'), ('s <= p', '<='), ('s == p', '='), ('s != p', '!='), ('s >= p0 and s <= p1', 'between')], max_length=255)),
                ('input', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iot.Sensor')),
                ('trigger', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conditions', to='iot.Trigger')),
            ],
            bases=(core.utils.models.ValidateOnSaveMixin, models.Model),
        ),
        migrations.CreateModel(
            name='TriggerAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('output_value', models.FloatField()),
                ('output_pk', models.PositiveIntegerField()),
                ('output_type', models.ForeignKey(limit_choices_to=models.Q(models.Q(('app_label', 'iot'), ('model', 'pid')), models.Q(('app_label', 'iot'), ('model', 'actuator')), _connector='OR'), on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('trigger', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='iot.Trigger')),
            ],
        ),
        migrations.CreateModel(
            name='SensorFusion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('strategy', models.CharField(choices=[('iot.fusion.sampling.HighSampling', 'High Sampling'), ('iot.fusion.ldr.Lumen', 'Electric Tension to Lumen using a LDR'), ('iot.fusion.ldr.Lux', 'Electric Tension to Lux using a LDR'), ('iot.fusion.thermistor.SteinhartHart', 'Temperatude with Steinhart-Hart (NTC Thermistor) '), ('iot.fusion.thermistor.BetaFactor', 'Temperatude with Beta Factor (NTC Thermistor) '), ('iot.fusion.filter.LowPass', 'Low Pass Filter')], max_length=255, verbose_name='Fusion strategy')),
                ('strategy_options', jsonfield.fields.JSONField(blank=True, default={}, null=True)),
                ('inputs', models.ManyToManyField(related_name='consumers', to='iot.Sensor')),
                ('output', models.OneToOneField(help_text='Output virtual sensor', limit_choices_to={'is_virtual': True}, on_delete=django.db.models.deletion.CASCADE, related_name='origin', to='iot.Sensor', verbose_name='Output sensor')),
            ],
            options={
                'verbose_name': 'Sensor Fusion',
                'ordering': ('output__name',),
            },
        ),
        migrations.CreateModel(
            name='SensorData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('value', models.FloatField()),
                ('raw', jsonfield.fields.JSONField(blank=True, null=True)),
                ('measure_unit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='data', to='iot.MeasureUnit')),
                ('position', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='data', to='iot.Position')),
                ('sensor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data', to='iot.Sensor')),
            ],
            options={
                'verbose_name': 'Sensor Data',
                'ordering': ('-time',),
            },
            bases=(core.utils.models.ValidateOnSaveMixin, models.Model),
        ),
        migrations.CreateModel(
            name='PID',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('active', models.BooleanField(default=True)),
                ('inverse', models.BooleanField(default=False)),
                ('error', models.FloatField(default=0)),
                ('integral', models.FloatField(default=0)),
                ('target', models.FloatField()),
                ('kp', models.FloatField()),
                ('ki', models.FloatField()),
                ('kd', models.FloatField()),
                ('input', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pid_controllers', to='iot.Sensor')),
                ('output', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pid_controllers', to='iot.Actuator')),
            ],
            options={
                'verbose_name': 'PID',
                'ordering': ('-active', 'name'),
            },
        ),
        migrations.CreateModel(
            name='ActuatorData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('value', models.FloatField()),
                ('raw', jsonfield.fields.JSONField(blank=True, null=True)),
                ('actuator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data', to='iot.Actuator')),
                ('measure_unit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='iot.MeasureUnit')),
                ('position', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='iot.Position')),
            ],
            options={
                'verbose_name': 'Actuator Data',
                'ordering': ('-time',),
            },
        ),
        migrations.AddField(
            model_name='actuator',
            name='magnitude',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iot.Magnitude'),
        ),
        migrations.AddField(
            model_name='actuator',
            name='measure_unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='iot.MeasureUnit'),
        ),
        migrations.AddField(
            model_name='actuator',
            name='position',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='actuator', to='iot.Position'),
        ),
        migrations.CreateModel(
            name='ConversionFormula',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('formula', models.TextField()),
                ('from_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_formulas', to='iot.MeasureUnit')),
                ('to_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_formulas', to='iot.MeasureUnit')),
            ],
            options={
                'verbose_name': 'Conversion Formula',
                'ordering': ('from_unit__name', 'to_unit__name'),
                'unique_together': {('from_unit', 'to_unit')},
            },
        ),
    ]
