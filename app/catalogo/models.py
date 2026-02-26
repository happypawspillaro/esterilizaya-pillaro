from django.db import models
from esterilizaya.constantes import (
    CATEGORIA_SERVICIO,
    ESPECIE,
    TIPO_MEDICINA_CATEGORIAS,
)


class Servicio(models.Model):
    """Catálogo global de servicios (ej. esterilización, consulta, etc.)."""

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    categoria = models.CharField(
        max_length=4,
        choices=CATEGORIA_SERVICIO,
    )
    # Precios por defecto sugeridos
    default_costo_veterinario = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Costo veterinario por defecto"
    )
    default_precio_publico = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Precio público por defecto"
    )
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """Catálogo global de productos/servicios."""

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    especie_objetivo = models.CharField(max_length=1, choices=ESPECIE, blank=True, null=True)
    tipo_medicina = models.CharField(max_length=4, choices=TIPO_MEDICINA_CATEGORIAS, blank=True, null=True)
    peso_recomendado = models.PositiveSmallIntegerField()
    default_precio_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    default_precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self) -> str:
        return f"{self.nombre}"
