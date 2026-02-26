from catalogo.models import Producto, Servicio
from django.contrib import admin


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "default_precio_venta", "default_precio_compra", "tipo_medicina")
    search_fields = ("nombre", "tipo_medicina")
    list_filter = ("tipo_medicina",)


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "default_precio_publico", "default_costo_veterinario", "categoria")
    search_fields = ("nombre", "categoria")
    list_filter = ("categoria",)
