from django.http import JsonResponse
from django.templatetags.static import static


from .models import Product, Order

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

import phonenumbers

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


@api_view(['POST'])
def register_order(request):
    order_content = request.data

    if 'firstname' not in order_content or not order_content['firstname'] or not isinstance(order_content['firstname'], str):
        content = {'error': 'They key \'firstname\' is not specified or not str.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    if 'lastname' not in order_content or not order_content['lastname'] or not isinstance(order_content['lastname'], str):
        content = {'error': 'They key \'lastname\' is not specified or not str.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    if 'address' not in order_content or not order_content['address'] or not isinstance(order_content['address'], str):
        content = {'error': 'They key \'firstname\' is not specified or not str.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    if 'phonenumber' not in order_content or not order_content['phonenumber']:
        content = {'error': 'The key \'phonenumber\' is not specified.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    parsed_number = phonenumbers.parse(order_content['phonenumber'], "RU")
    if not phonenumbers.is_valid_number(parsed_number):
        content = {'error': 'Phone number is not correct.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    if 'products' not in order_content or not order_contnet['products'] or not isinstance(order_content['products'], list):
        content = {'error': 'Key \'products\' is not specified or not list.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    for item in order_content['products']:
        key = item['product']
        if not Product.objects.filter(pk=key).exists():
            content = {'error': f'Key {key} does not exist in \'products\'.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.create(
        first_name = order_content['firstname'],
        last_name = order_content['lastname'],
        phone_number = order_content['phonenumber'],
        address = order_content['address'],
    )
    for item in order_content['products']:
        product = Product.objects.filter(pk=item['product']).get()
        for _ in range(item['quantity']):
            order.products.add(product)
    return Response({})
