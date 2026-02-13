from catalogo.models import ProductoBase
from django.contrib import admin


# Register your models here.
@admin.register(ProductoBase)
class CatalogoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio_publico_defecto", "precio_interno_defecto")
    search_fields = ("nombre",)  # Necessary for autocomplete
