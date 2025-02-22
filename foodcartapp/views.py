from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        Serializer, ValidationError)

from .models import Order, OrderItem, Product


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def validate(data):
    errors = []
    for item in data['products']:
        key = item['product']
        if not Product.objects.filter(pk=key).exists():
            error_message = f'The key {key} does not exist in \'products\''
            errors.append(error_message)

    if errors:
        raise ValidationError(errors)


class ProductsSerializer(Serializer):
    product = IntegerField()
    quantity = IntegerField()

    def validate_product(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise ValidationError(f'Недопустимый первичный ключ {value}')
        return value


class OrderSerializer(ModelSerializer):
    products = ProductsSerializer(
        many=True,
        allow_empty=False,
        write_only=True
    )

    class Meta:
        model = Order
        fields = '__all__'


@api_view(['POST'])
@transaction.atomic
def register_order(request):

    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    order = Order.objects.create(
        firstname=serializer.validated_data['firstname'],
        lastname=serializer.validated_data['lastname'],
        phonenumber=serializer.validated_data['phonenumber'],
        address=serializer.validated_data['address'],
    )

    item_fields = serializer.validated_data['products']

    order_items = [
        OrderItem(
            product=Product.objects.get(pk=item_field['product']),
            order=order,
            price=Product.objects.get(pk=item_field['product']).price,
            quantity=item_field['quantity'],
        ) for item_field in item_fields
    ]

    OrderItem.objects.bulk_create(order_items)

    content = OrderSerializer(order).data

    return Response(content)
