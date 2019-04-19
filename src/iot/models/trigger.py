from .io import Sensor
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.manager import BaseManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from jsonfield import JSONField
from core.utils.models import ValidateOnSaveMixin
from functools import reduce
from pydoc import locate
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _



class TriggerCondition(ValidateOnSaveMixin, models.Model):
    input = models.ForeignKey(
        'Sensor',
        on_delete=models.CASCADE,
    )

    params = JSONField(

    )

    check_script = models.CharField(
        max_length=255,
        choices=(
            ('s > p', _('>')),
            ('s >= p', _('>=')),
            ('s < p', _('<')),
            ('s <= p', _('<=')),
            ('s == p', _('=')),
            ('s != p', _('!=')),
            ('s >= p0 and s <= p1', _('between')),
        )
    )

    trigger = models.ForeignKey(
        'Trigger',
        on_delete=models.CASCADE,
        related_name='conditions',
    )

    def clean(self):
        try:
            self.check_condition(0.0)
        except Exception as ex:
            raise ValidationError({
                'params': ex.message,
                'check_script': ex.message,
            })

    def check_condition(self, sensor_value=None):
        if sensor_value is None:
            sensor_value = self.input.value
        params = self.params
        if isinstance(params, dict):
            params = params
        elif isinstance(params, list):
            params = dict([('p%d' % k, v)
                           for k, v in zip(range(len(params)), params)])
        else:
            params = dict(p=params)
        params.update(dict(s=sensor_value))
        return eval(self.check_script, {}, params)


class TriggerAction(models.Model):
    output_type_queryset = models.Q(
        app_label='iot', model='pid'
    ) | models.Q(
        app_label='iot', model='actuator'
    )

    output_value = models.FloatField(

    )

    output_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=output_type_queryset,
    )

    output_pk = models.PositiveIntegerField(

    )

    output = GenericForeignKey('output_type', 'output_pk')

    trigger = models.ForeignKey(
        'Trigger',
        on_delete=models.CASCADE,
        related_name='actions',
    )

    def do_action(self):
        self.output.value = self.output_value


class TriggerQuerySet(models.QuerySet):
    pass


class TriggerManager(BaseManager.from_queryset(TriggerQuerySet)):
    pass


class Trigger(models.Model):

    objects = TriggerManager()

    active = models.BooleanField(
        default=True,
    )

    name = models.CharField(
        max_length=255,
        unique=True,
    )

    reduce_operator = models.CharField(
        max_length=255,
        choices=(
            ('operator.and_', _('And')),
            ('operator.or_', _('Or')),
        )
    )

    def check_conditions(self):
        results = [condition.check_condition()
                   for condition in self.conditions.all()]
        return reduce(locate(self.reduce_operator), results)

    def try_fire(self):
        if not self.check_conditions():
            return
        for action in self.actions.all():
            action.do_action()
