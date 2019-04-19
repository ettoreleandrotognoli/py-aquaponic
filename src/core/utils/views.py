import operator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from functools import reduce
from rest_framework.serializers import ValidationError


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
