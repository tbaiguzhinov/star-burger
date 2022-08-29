# Generated by Django 3.2 on 2022-08-29 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0003_auto_20220827_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='lat',
            field=models.FloatField(blank=True, null=True, verbose_name='Широта'),
        ),
        migrations.AlterField(
            model_name='location',
            name='lon',
            field=models.FloatField(blank=True, null=True, verbose_name='Долгота'),
        ),
    ]
