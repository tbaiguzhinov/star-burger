from django.http import JsonResponse
from django.templatetags.static import static


from .models import Product, Order

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

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

    if 'products' not in order_content:
        content = {'products': 'Обязательное поле.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    if isinstance(order_content['products'], str):
        content = {'products': 'Ожидался list со значениями, но был получен str.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    if order_content['products'] is None:
        content = {'products': 'Это поле не может быть пустым.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    if not order_content['products']:
        content = {'products': 'Этот список не может быть пустым.'}
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
