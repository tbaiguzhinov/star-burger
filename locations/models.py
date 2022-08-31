from django.db import models
from django.utils import timezone


class Location(models.Model):

    address = models.CharField(
        'Адрес',
        max_length=200,
        unique=True,
        db_index=True,
    )
    lon = models.FloatField(
        'Долгота',
        null=True,
        blank=True,
    )
    lat = models.FloatField(
        'Широта',
        null=True,
        blank=True,
    )
    geocoder_req_date = models.DateTimeField(
        'Дата последнего запроса к геокодеру',
        default=timezone.now,
    )

    class Meta:
        verbose_name = 'адрес'
        verbose_name_plural = 'адреса'

    def __str__(self):
        return self.address
