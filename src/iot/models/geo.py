from __future__ import annotations
from typing import Tuple
from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _


class PositionQuerySet(models.QuerySet):
    pass


class PositionManager(BaseManager.from_queryset(PositionQuerySet)):
    pass


class Position(models.Model):

    objects = PositionManager()

    class Meta:
        verbose_name = _('Position')

    latitude = models.FloatField(
        verbose_name=_('Latitude'),
    )

    longitude = models.FloatField(
        verbose_name=_('Longitude'),
    )

    altitude = models.FloatField(
        verbose_name=_('Altitude'),
    )

    def __str__(self) -> str:
        return '%f° %f° %f' % (self.latitude, self.longitude, self.altitude)

    def as_tuple(self) -> Tuple[float, float, float]:
        return self.latitude, self.longitude, self.altitude

    @classmethod
    def from_tuple(cls, t: Tuple[float, float, float]) -> Position:
        return cls(
            latitude=t[0],
            longitude=t[1],
            altitude=t[2],
        )
