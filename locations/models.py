from django.db import models
from django.utils import timezone
from geopy import distance


def measure_distance(coordinates1, coordinates2):
    coordinates1 = (coordinates1[1], coordinates1[0])
    coordinates2 = (coordinates2[1], coordinates2[0])
    return distance.distance(coordinates1, coordinates2).km


class Location(models.Model):

    address = models.CharField(
        'Адрес',
        max_length=200,
        unique=True,
        db_index=True,
    )
    lon = models.FloatField(
        'Долгота',
    )
    lat = models.FloatField(
        'Широта',
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
