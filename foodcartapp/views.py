from django.http import JsonResponse
from django.templatetags.static import static


from .models import Product, Order, OrderItem

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import Serializer
from rest_framework.serializers import IntegerField

from django.db import transaction


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
    products = ProductsSerializer(many=True, allow_empty=False, write_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'


@api_view(['POST'])
@transaction.atomic
def register_order(request):
    
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    order = Order.objects.create(
        firstname = serializer.validated_data['firstname'],
        lastname = serializer.validated_data['lastname'],
        phonenumber = serializer.validated_data['phonenumber'],
        address = serializer.validated_data['address'],
    )

    for item in serializer.validated_data['products']:
        product = Product.objects.filter(pk=item['product']).get()
        OrderItem.objects.create(
            product = product,
            order = order,
            price = product.price,
            quantity = item['quantity'],
        )
    
    content = OrderSerializer(order).data

    return Response(content)
