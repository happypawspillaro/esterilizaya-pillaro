from catalogo.models import Producto, Servicio
from django.conf import settings
from django.db import models
from esterilizaya.constantes import TIPOS_PAGO
from registro.models import Registro


class Pago(models.Model):
    """Registro de pago realizado."""

    registro = models.OneToOneField(Registro, on_delete=models.CASCADE, related_name="pago")
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    metodo = models.CharField(
        max_length=4,
        choices=TIPOS_PAGO,
        default="EFE",
    )
    notas = models.TextField(blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario que facturó"
    )

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self):
        return f"Pago {self.id} - {self.registro.nombre} - ${self.monto_total}"


class PagoServicio(models.Model):
    """Servicio incluido en un pago (ej. esterilización)."""

    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name="servicios")
    servicio = models.ForeignKey(Servicio, on_delete=models.SET_NULL, null=True, blank=True)
    nombre_servicio = models.CharField(max_length=200, blank=True)  # snapshot
    descripcion = models.CharField(max_length=200, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio público")
    costo_veterinario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo veterinario")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario que facturó"
    )

    class Meta:
        verbose_name = "Servicio en pago"
        verbose_name_plural = "Servicios en pago"

    def __str__(self):
        return f"{self.nombre_servicio or self.servicio} - ${self.precio}"


class PagoProducto(models.Model):
    """Producto (medicamento) incluido en un pago."""

    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name="productos")
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True)
    nombre_producto = models.CharField(max_length=200, blank=True)  # snapshot
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio público unitario")
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo unitario")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario que facturó"
    )

    class Meta:
        verbose_name = "Producto en pago"
        verbose_name_plural = "Productos en pago"

    def __str__(self):
        return f"{self.nombre_producto or self.producto} x{self.cantidad}"


class PagoExtra(models.Model):
    """Extra veterinario (procedimiento adicional). Solo precio (el costo se asigna después manualmente si existe)."""

    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name="extras")
    descripcion = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio público")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario que facturó"
    )

    class Meta:
        verbose_name = "Extra en pago"
        verbose_name_plural = "Extras en pago"

    def __str__(self):
        return f"Extra: {self.descripcion} - ${self.precio}"


class PagoOtro(models.Model):
    """Otros conceptos diversos. Solo precio."""

    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name="otros")
    descripcion = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio público")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario que facturó"
    )

    class Meta:
        verbose_name = "Otro en pago"
        verbose_name_plural = "Otros en pago"

    def __str__(self):
        return f"Otro: {self.descripcion} - ${self.precio}"
