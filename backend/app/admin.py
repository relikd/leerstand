from django.contrib import admin
from django.contrib.auth.models import Group  # , User

from app.models import City, Place

# admin.site.register(Place, )

#############################
# Django defaults
#############################

admin.site.site_header = 'Leerstand-Verwaltung'  # top-most title
admin.site.index_title = 'Leerstand'  # title at root
admin.site.site_title = 'Leerstand-Verwaltung'  # suffix to <title>

admin.site.unregister(Group)
# admin.site.unregister(User)


#############################
# App adjustments
#############################

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'place_count', 'center', 'zoom']

    def get_readonly_fields(self, request, obj=None):
        return ['name'] if obj else []

    @admin.display(description='Orte')
    def place_count(self, instance: 'City'):
        return instance.places.count()


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['address', 'city', 'since', 'until', 'created', 'updated']
    list_filter = ['city']
    search_fields = ['address', 'description']
    ordering = ['-updated']
