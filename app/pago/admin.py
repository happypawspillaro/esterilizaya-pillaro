from django.contrib import admin

from .models import Pago, PagoExtra, PagoOtro, PagoProducto, PagoServicio

# --- Inlines para mostrar detalles dentro del Pago ---


class PagoServicioInline(admin.TabularInline):
    model = PagoServicio
    extra = 0
    readonly_fields = ("servicio", "nombre_servicio", "descripcion", "precio", "costo_veterinario")
    can_delete = False
    verbose_name = "Servicio"
    verbose_name_plural = "Servicios"


class PagoProductoInline(admin.TabularInline):
    model = PagoProducto
    extra = 0
    readonly_fields = ("producto", "nombre_producto", "cantidad", "precio_unitario", "costo_unitario")
    can_delete = False
    verbose_name = "Producto"
    verbose_name_plural = "Productos"


class PagoExtraInline(admin.TabularInline):
    model = PagoExtra
    extra = 0
    readonly_fields = ("descripcion", "precio")
    can_delete = False
    verbose_name = "Extra"
    verbose_name_plural = "Extras"


class PagoOtroInline(admin.TabularInline):
    model = PagoOtro
    extra = 0
    readonly_fields = ("descripcion", "precio")
    can_delete = False
    verbose_name = "Otro"
    verbose_name_plural = "Otros"


# --- Administrador principal de Pago ---


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("id", "registro_mascota", "monto_total", "fecha_pago", "metodo", "usuario")
    list_filter = ("metodo", "fecha_pago", "usuario")
    search_fields = ("registro__mascota_name", "notas", "usuario__username")
    readonly_fields = ("fecha_pago",)
    fieldsets = (
        (None, {"fields": ("registro", "monto_total", "metodo", "notas", "usuario")}),
        ("Información de tiempo", {"fields": ("fecha_pago",), "classes": ("collapse",)}),
    )
    inlines = [PagoServicioInline, PagoProductoInline, PagoExtraInline, PagoOtroInline]

    def registro_mascota(self, obj):
        return obj.registro.mascota_name

    registro_mascota.short_description = "Mascota"


# --- Administradores individuales para cada detalle (opcional) ---


@admin.register(PagoServicio)
class PagoServicioAdmin(admin.ModelAdmin):
    list_display = ("id", "pago", "servicio", "nombre_servicio", "precio", "costo_veterinario")
    list_filter = ("pago__fecha_pago",)
    search_fields = ("nombre_servicio", "descripcion", "pago__registro__mascota_name")
    raw_id_fields = ("pago", "servicio")


@admin.register(PagoProducto)
class PagoProductoAdmin(admin.ModelAdmin):
    list_display = ("id", "pago", "producto", "nombre_producto", "cantidad", "precio_unitario", "costo_unitario")
    list_filter = ("pago__fecha_pago",)
    search_fields = ("nombre_producto", "pago__registro__mascota_name")
    raw_id_fields = ("pago", "producto")


@admin.register(PagoExtra)
class PagoExtraAdmin(admin.ModelAdmin):
    list_display = ("id", "pago", "descripcion", "precio")
    list_filter = ("pago__fecha_pago",)
    search_fields = ("descripcion", "pago__registro__mascota_name")
    raw_id_fields = ("pago",)


@admin.register(PagoOtro)
class PagoOtroAdmin(admin.ModelAdmin):
    list_display = ("id", "pago", "descripcion", "precio")
    list_filter = ("pago__fecha_pago",)
    search_fields = ("descripcion", "pago__registro__mascota_name")
    raw_id_fields = ("pago",)
