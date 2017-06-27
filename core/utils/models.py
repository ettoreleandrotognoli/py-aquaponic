# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import decimal

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import FloatField


class ValidateOnSaveMixin(object):
    def save(self, *args, **kwargs):
        self.full_clean()
        return super(ValidateOnSaveMixin, self).save(*args, **kwargs)


class DecimalField(FloatField):
    def __int__(self, *args, **kwargs):
        super(DecimalField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        value = super(FloatField, self).get_prep_value(value)
        if value is None:
            return None
        return decimal.Decimal(value)

    def to_python(self, value):
        if value is None:
            return value
        try:
            return decimal.Decimal(value)
        except (TypeError, ValueError):
            raise DjangoValidationError(
                self.error_messages['invalid'],
                code='invalid',
                params={'value': value},
            )
