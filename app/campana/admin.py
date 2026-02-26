from django.contrib import admin

from .models import Campana, ProductoCampana, ServicioCampana


class ProductoCampanaInline(admin.TabularInline):
    model = ProductoCampana
    extra = 1
    verbose_name = "Producto en campaña"
    verbose_name_plural = "Productos en campaña"


class ServicioCampanaInline(admin.TabularInline):
    model = ServicioCampana
    extra = 1
    verbose_name = "Servicio en campaña"
    verbose_name_plural = "Servicios en campaña"


@admin.register(Campana)
class CampanaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "fecha", "barrio", "parroquia"]
    list_filter = ["barrio", "parroquia"]
    ordering = ["fecha"]
    show_facets = admin.ShowFacets.ALWAYS
    inlines = [ServicioCampanaInline, ProductoCampanaInline]
