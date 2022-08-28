from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from locations.models import get_coordinates, measure_distance


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


class OrderQuerySet(models.QuerySet):

    def get_order_value(self):
        return self.annotate(
            total=Sum(F('items__price')*F('items__quantity'))
        )

    def get_closest_restaurants(self):
        rest_items = RestaurantMenuItem.objects.filter(
            availability=True
        ).prefetch_related('product').prefetch_related('restaurant')
        for order in self:
            order_coordinates = get_coordinates(order.address)
            if not order_coordinates:
                continue
            order_items = order.items.prefetch_related('product')
            restaurants_per_item = []
            for order_item in order_items.iterator():
                restaurants_per_item.append([
                    rest_item.restaurant for rest_item in rest_items.iterator()
                    if rest_item.product.id == order_item.product.id
                ])
            available_restaurants = set(restaurants_per_item[0]).intersection(
                *restaurants_per_item
            )
            restaurants_with_distance = []
            for restaurant in available_restaurants:
                rest_coordinates = get_coordinates(restaurant.address)
                distance = measure_distance(
                    order_coordinates, rest_coordinates
                )
                restaurants_with_distance.append(
                    {
                        'name': restaurant.name,
                        'distance': distance
                    }
                )
            order.restaurants = sorted(
                restaurants_with_distance,
                key=lambda restaurant: restaurant['distance']
            )
        return self


class Order(models.Model):
    STATUS_CHOICES = [
        ("1", 'Необработанный'),
        ("2", 'В сборке'),
        ("3", 'Передан в доставку'),
        ("4", 'Завершен'),
    ]
    PAYMENT_CHOICES = [
        ("1", 'Не выбрано'),
        ("2", 'Наличными'),
        ("3", 'Электронно'),
    ]

    firstname = models.CharField('Имя', max_length=50)
    lastname = models.CharField('Фамилия', max_length=50)
    phonenumber = PhoneNumberField('Номер телефона', db_index=True)
    address = models.CharField('Адрес доставки', max_length=100)
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
        related_name='items',
        on_delete=models.CASCADE,
    )
    order = models.ForeignKey(
        Order,
        verbose_name='заказ',
        related_name='items',
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
        validators=[MinValueValidator(1)],
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
