# Generated by Django 3.2 on 2022-07-25 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_product_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='total',
            field=models.FloatField(null=True, verbose_name='сумма заказа'),
        ),
    ]
