# Generated by Django 3.2 on 2022-08-03 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0048_auto_20220803_1332'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_option',
            field=models.CharField(choices=[('1', 'Не выбрано'), ('2', 'Наличными'), ('3', 'Электронно')], default='1', max_length=50, verbose_name='Способ оплаты'),
        ),
    ]
