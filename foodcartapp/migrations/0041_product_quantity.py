# Generated by Django 3.2 on 2022-07-24 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_auto_20220724_1720'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='quantity',
            field=models.IntegerField(blank=True, default=1, verbose_name='количество'),
        ),
    ]
