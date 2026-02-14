from catalogo.models import ProductoBase
from django.contrib import admin


# Register your models here.
@admin.register(ProductoBase)
class CatalogoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio_publico", "costo")
    search_fields = ("nombre",)  # Necessary for autocomplete
