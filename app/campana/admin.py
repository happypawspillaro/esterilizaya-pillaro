from django.contrib import admin

from .models import Campana, ItemCampana


class ItemCampanaInline(admin.TabularInline):
    model = ItemCampana
    extra = 1  # Shows one empty row for adding items
    fields = ("producto", "costo", "precio_publico")  # Layout in the table


# Register your models here.
@admin.register(Campana)
class CampanaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "fecha", "barrio", "parroquia"]
    list_filter = ["barrio", "parroquia"]
    ordering = ["fecha"]
    show_facets = admin.ShowFacets.ALWAYS
    inlines = [ItemCampanaInline]
