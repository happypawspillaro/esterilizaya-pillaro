import logging

from catalogo.models import ProductoBase
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from esterilizaya.constantes import (
    CANTONES,
    MAX_LONG_BARRIOS,
    MAX_LONG_CANTONES,
    MAX_LONG_PARROQUIAS,
    PARROQUIAS,
)

logger = logging.getLogger(__name__)


class ActivasManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(estado=Campana.Estado.ACTIVA)


class PasadasManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(estado=Campana.Estado.PASADA)


class Campana(models.Model):
    """Modelo inicial sobre la campaña"""

    class Estado(models.TextChoices):
        ACTIVA = "AC", "Activa"
        PASADA = "PA", "Pasada"

    class Meta:
        ordering = ["fecha"]

    nombre = models.CharField(max_length=250)
    canton = models.CharField(
        choices=CANTONES, max_length=MAX_LONG_CANTONES, default="PI", help_text="Cantón donde se desarrolla la campaña"
    )
    parroquia = models.CharField(
        choices=PARROQUIAS,
        max_length=MAX_LONG_PARROQUIAS,
        unique_for_date="creada",
        help_text="Parroquia donde se desarrolla la campaña",
    )
    barrio = models.CharField(max_length=MAX_LONG_BARRIOS, help_text="Barrio donde se desarrolla la campaña")
    fecha = models.DateField(help_text="Fecha de desarrollo de la campaña")
    n_animales = models.PositiveSmallIntegerField(
        help_text="Mínimo 20 y máximo 50 animales", validators=[MaxValueValidator(50), MinValueValidator(1)]
    )
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=2, choices=Estado, default=Estado.ACTIVA)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="campana")
    objects = models.Manager()
    activas = ActivasManager()
    pasadas = PasadasManager()

    def __str__(self) -> str:
        return self.nombre

    def get_absolute_url(self):
        return reverse("campana:mostrar", args=[self.fecha.year, self.parroquia, self.fecha.month, self.fecha.day])


class ItemCampana(models.Model):
    campana = models.ForeignKey(Campana, on_delete=models.CASCADE)
    # Previene eliminar un producto que se ha usado en una campaña,
    # lo cual es importante para mantener la integridad histórica de los datos.
    producto = models.ForeignKey(ProductoBase, on_delete=models.PROTECT)
    # Guardamos los costos reales usados en esta campaña, lo cual es crucial para mantener la integridad histórica #
    # de los datos, incluso si los precios en el catálogo cambian posteriormente.
    costo = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    precio_publico = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    def __str__(self):
        return f"{self.producto.nombre} @ {self.campana.nombre}"
