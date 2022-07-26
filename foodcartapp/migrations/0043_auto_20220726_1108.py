# Generated by Django 3.2 on 2022-07-26 05:08

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0042_order_total'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='total',
        ),
        migrations.RemoveField(
            model_name='product',
            name='order',
        ),
        migrations.RemoveField(
            model_name='product',
            name='quantity',
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Цена товара')),
                ('quantity', models.IntegerField(verbose_name='Количество')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orderitems', to='foodcartapp.order', verbose_name='заказ')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orderitems', to='foodcartapp.product', verbose_name='товар')),
            ],
            options={
                'verbose_name': 'пункт заказа',
                'verbose_name_plural': 'пункты заказа',
            },
        ),
    ]
