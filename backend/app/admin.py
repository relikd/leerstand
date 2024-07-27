from django.contrib import admin
from django.contrib.auth.models import Group  # , User

from app.models import Place

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

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['address', 'since', 'until', 'created', 'updated']
    search_fields = ['address', 'description']
    ordering = ['-updated']
