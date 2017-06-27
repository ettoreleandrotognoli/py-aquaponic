# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.serializers import ValidationError

import decimal
import operator
from collections import Iterable
from django.conf.urls import url
from django.db.models import Q, FloatField
from django.shortcuts import get_object_or_404
from functools import reduce


def make_url(urlpatterns, default_decorator=[]) -> type:
    class URL(object):
        def __init__(self, regex, name=None, decorator=None, **kwargs):
            self.regex = regex
            self.name = name
            self.kwargs = kwargs
            self.decorator = decorator

        def __call__(self, view):
            django_view = view if getattr(view, 'as_view', False) is False else view.as_view()
            if isinstance(default_decorator, Iterable):
                for dec in default_decorator:
                    django_view = dec(django_view)
            elif default_decorator is not None:
                django_view = default_decorator(django_view)
            if isinstance(self.decorator, Iterable):
                for dec in self.decorator:
                    django_view = dec(django_view)
            elif self.decorator is not None:
                django_view = self.decorator(django_view)
            urlpatterns.append(
                url(
                    self.regex,
                    django_view,
                    name=self.name,
                    kwargs=self.kwargs
                )
            )
            return view

    return URL


class MultipleFieldLookupMixin(object):
    def get_object(self):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        queryset_filter = {}
        fields = [f for f in self.lookup_field if f in self.kwargs]
        for field in fields:
            queryset_filter[field] = self.kwargs[field]
        q = reduce(operator.or_, (Q(x) for x in queryset_filter.items()))
        return get_object_or_404(queryset, q)


class ValidateOnSaveMixin(object):
    def save(self, *args, **kwargs):
        self.full_clean()
        return super(ValidateOnSaveMixin, self).save(*args, **kwargs)


class TrapDjangoValidationErrorMixin(object):
    def perform_create(self, serializer):
        try:
            super(TrapDjangoValidationErrorMixin, self).perform_create(serializer)
        except DjangoValidationError as detail:
            raise ValidationError(detail.message_dict)

    def perform_update(self, serializer):
        try:
            instance = serializer.save()
        except DjangoValidationError as detail:
            raise ValidationError(detail.message_dict)


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
