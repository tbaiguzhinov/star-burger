from django.contrib import admin

from locations.models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    pass
