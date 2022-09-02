import requests
from django.conf import settings
from geopy import distance

from locations.models import Location


def measure_distance(coordinates1, coordinates2):
    lon1, lat1 = coordinates1
    lon2, lat2 = coordinates2
    return distance.distance((lat1, lon1), (lat2, lon2)).km


def get_coordinates(address, locations):
    for location in locations:
        if location.address == address:
            return location.lon, location.lat

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
