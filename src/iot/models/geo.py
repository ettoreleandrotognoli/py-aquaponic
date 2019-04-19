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


