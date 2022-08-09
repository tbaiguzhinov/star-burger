from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import F, Sum

import requests
from geopy import distance

from django.conf import settings

from locations.models import Location


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


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
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

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


def measure_distance(coordinates1, coordinates2):
    coordinates1 = (coordinates1[1], coordinates1[0])
    coordinates2 = (coordinates2[1], coordinates2[0])
    return distance.distance(coordinates1, coordinates2).km


class OrderQuerySet(models.QuerySet):
    
    def get_total(self):
        return self.annotate(total=Sum(F('orderitems__price')*F('orderitems__quantity')))

    def get_restaurants(self):
        rest_menu_items = RestaurantMenuItem.objects.filter(availability=True).prefetch_related('product').prefetch_related('restaurant')
        for order in self:
            order_coordinates = get_coordinates(order.address)
            if not order_coordinates:
                continue
            order_items = order.orderitems.prefetch_related('product')
            restaurants_per_item = []
            for order_item in order_items.iterator():
                restaurants_per_item.append([rest_menu_item.restaurant for rest_menu_item in rest_menu_items.iterator() if rest_menu_item.product.id == order_item.product.id])
            available_restaurants = set(restaurants_per_item[0]).intersection(*restaurants_per_item)
            restaurants_with_disntance = []
            for restaurant in available_restaurants:
                rest_coordinates = get_coordinates(restaurant.address)
                distance = measure_distance(order_coordinates, rest_coordinates)
                restaurants_with_disntance.append(
                    {
                        'name': restaurant.name,
                        'distance': distance
                    }
                )
            order.restaurants = sorted(restaurants_with_disntance, key=lambda restaurant: restaurant['distance']) 
        return self


class Order(models.Model):
    firstname = models.CharField('Имя', max_length=50)
    lastname = models.CharField('Фамилия', max_length=50)
    phonenumber = PhoneNumberField('Номер телефона', db_index=True)
    address = models.CharField('Адрес доставки', max_length=100)
    STATUS_CHOICES = [
        ("1", 'Необработанный'),
        ("2", 'В сборке'),
        ("3", 'Передан в доставку'),
        ("4", 'Завершен'),
    ]
    status = models.CharField(
        'Статус',
        max_length=50,
        choices=STATUS_CHOICES,
        default="1",
        db_index=True,
    )
    comment = models.TextField(
        'Комментарий',
        blank=True,
    )
    registered_at = models.DateTimeField(
        'Время и дата регистрации',
        default=timezone.now,
        db_index=True,
    )
    called_at = models.DateTimeField(
        'Время и дата звонка оператора',
        blank=True,
        null=True,
        db_index=True,
    )
    delivered_at = models.DateTimeField(
        'Время и дата доставки',
        blank=True,
        null=True,
        db_index=True,
    )
    PAYMENT_CHOICES = [
        ("1", 'Не выбрано'),
        ("2", 'Наличными'),
        ("3", 'Электронно'),
    ]
    payment_option = models.CharField(
        'Способ оплаты',
        max_length=50,
        choices=PAYMENT_CHOICES,
        default="1",
        db_index=True,
    )
    preparing_restaurant = models.ForeignKey(
        'Restaurant',
        related_name='orders',
        verbose_name='Готовит ресторан:',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.id}'


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class OrderItem(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name="товар",
        related_name='orderitems',
        on_delete=models.CASCADE,
    )
    order = models.ForeignKey(
        Order,
        verbose_name='заказ',
        related_name='orderitems',
        on_delete=models.CASCADE,
    )
    price = models.DecimalField(
        "Цена товара",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    quantity = models.IntegerField(
        'Количество',
    )

    class Meta:
        verbose_name = 'пункт заказа'
        verbose_name_plural = 'пункты заказа'

    def __str__(self):
        return f'{self.product} - {self.order}'


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name='ресторан',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f'{self.restaurant.name} - {self.product.name}'
