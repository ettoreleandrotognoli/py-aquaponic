import datetime

import iso8601
from django import forms as django_forms
from django.forms.fields import from_current_timezone
from django.utils import timezone


class ISO8601Field(django_forms.DateTimeField):
    def to_python(self, value):
        """
        Validates that the input can be converted to a datetime. Returns a
        Python datetime.datetime object.
        """
        if value in self.empty_values:
            return None
        if isinstance(value, datetime.datetime):
            return from_current_timezone(value)
        if isinstance(value, datetime.date):
            result = datetime.datetime(value.year, value.month, value.day)
            return from_current_timezone(result)
        result = iso8601.parse_date(value, default_timezone=timezone.get_current_timezone())
        return from_current_timezone(result)
