import requests
from django.conf import settings
from django.db import models
from django.utils import timezone
from geopy import distance


def measure_distance(coordinates1, coordinates2):
    lon1, lat1 = coordinates1
    lon2, lat2 = coordinates2
    return distance.distance((lat1, lon1), (lat2, lon2)).km


def get_coordinates(address):
    try:
        db_location = Location.objects.get(address=address)
        return (db_location.lon, db_location.lat)
    except Location.DoesNotExist:
        pass

    apikey = settings.YANDEX_KEY
    response = requests.get(
        "https://geocode-maps.yandex.ru/1.x",
        params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        }
    )
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection'][
        'featureMember'
    ]

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")

    Location.objects.create(
        address=address,
        lon=lon,
        lat=lat,
    )
    return lon, lat


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
