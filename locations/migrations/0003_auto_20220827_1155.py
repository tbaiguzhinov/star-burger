# Generated by Django 3.2 on 2022-08-27 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0002_alter_location_geocoder_req_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='location',
            options={'verbose_name': 'адрес', 'verbose_name_plural': 'адреса'},
        ),
        migrations.AlterField(
            model_name='location',
            name='address',
            field=models.CharField(db_index=True, max_length=200, unique=True, verbose_name='Адрес'),
        ),
    ]
