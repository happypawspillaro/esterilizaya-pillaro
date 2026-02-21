import uuid
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from campana.models import Producto, Servicio
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from esterilizaya.constantes import (
    AFIRMATIVO_NEGATIVO,
    CANTONES,
    COLORES,
    EDADES_ANOS,
    EDADES_MESES,
    ESPECIE,
    MAX_LONG_BARRIOS,
    MAX_LONG_CANTONES,
    MAX_LONG_PARROQUIAS,
    N_MASCOTAS,
    PARROQUIAS,
    RAZON_TENENCIA,
    SEXO,
)
from inscripcion.models import Inscripcion


def obtener_url_unico(instance, filename):
    current_date = datetime.now()
    year_folder = current_date.strftime("%y")
    month_folder = current_date.strftime("%m")
    day_folder = current_date.strftime("%d")

    # Crear la ruta en 'mascotas/%y/%m/%d/'
    extension = filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{extension}"
    return Path("mascotas") / year_folder / month_folder / day_folder / unique_filename


class Registro(models.Model):
    class Meta:
        unique_together = ("inscripcion", "numero_turno")
        verbose_name = "Registro"
        verbose_name_plural = "Registros"

        ordering = ["numero_turno"]
        indexes = [
            models.Index(fields=["-fecha_registro"]),
        ]

    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to=obtener_url_unico, blank=True, help_text="Foto de frente mascota a esterilizar")
    # Encabezado
    numero_turno = models.PositiveSmallIntegerField(
        help_text="Número turno entregado al tutor", validators=[MaxValueValidator(50), MinValueValidator(1)]
    )
    # Datos generales
    nombre = models.CharField(max_length=40, help_text="Nombre identificación mascota")
    color_principal = models.CharField(max_length=30, help_text="Color predominante mascota", choices=COLORES)
    color_secundario = models.CharField(
        max_length=30, help_text="Segundo color más frecuente mascota", blank=True, choices=COLORES
    )
    observaciones = models.CharField(
        max_length=200, blank=True, help_text="¿Celo? ¿Enfermedad? ¿Lactancia? ¿Encontrado calle?"
    )
    # Datos específicos
    especie = models.CharField(choices=ESPECIE, max_length=1, help_text="Especie mascota a esterilizar")
    sexo = models.CharField(choices=SEXO, max_length=2, help_text="Género mascota a esterilizar")
    edad_anos = models.PositiveSmallIntegerField(
        choices=EDADES_ANOS, default=0, verbose_name="Edad Años", help_text="Edad aproximada en años"
    )
    edad_meses = models.PositiveSmallIntegerField(
        choices=EDADES_MESES, default=6, verbose_name="Edad Meses", help_text="Edad aproximada en meses"
    )
    raza_mascota = models.CharField(max_length=65, help_text="Raza mascota, en caso de cruces poner Raza1/Raza2")
    carnet = models.CharField(
        choices=AFIRMATIVO_NEGATIVO,
        max_length=1,
        default="N",
        help_text="Vacunas para enfermedades caninas/felinas, rabia",
    )
    vulnerable = models.BooleanField(default=False, help_text="Indicar aquí si es un cupo gratuito")
    # Datos tutor
    nombres_tutor = models.CharField(max_length=250, help_text="Al menos un nombre y apellido tutor")
    numero_telefono_tutor = models.PositiveIntegerField(
        # Entre 7 y 10 dígitos
        validators=[MinValueValidator(1000000), MaxValueValidator(9999999999)],
        help_text="Teléfono celular o convencional, en caso de no haber escribe 0900000000",
    )
    cedula_identidad = models.PositiveIntegerField(
        validators=[MaxValueValidator(9999999999)], help_text="Número de diez dígitos, en caso de no haber 1800000000"
    )
    razon_tenencia = models.CharField(
        choices=RAZON_TENENCIA, max_length=2, default="CO", help_text="Por estadística, ¿Por qué lo tiene?"
    )
    canton_tutor = models.CharField(
        choices=CANTONES, max_length=MAX_LONG_CANTONES, help_text="Cantón residencia mascota", default="PI"
    )
    parroquia_tutor = models.CharField(
        choices=PARROQUIAS, max_length=MAX_LONG_PARROQUIAS, help_text="Parroquia residencia mascota"
    )
    barrio_tutor = models.CharField(max_length=MAX_LONG_BARRIOS, help_text="Barrio residencia mascota")
    # Porcentaje esterilización
    n_animales_hogar = models.SmallIntegerField(
        choices=N_MASCOTAS, default="3", help_text="Total perros y gatos en el hogar"
    )
    n_animales_hogar_esterilizadas = models.SmallIntegerField(
        choices=N_MASCOTAS, default="0", help_text="Total perros y gatos esterilizados en el hogar"
    )
    peso = models.FloatField(
        help_text="Valor entre 0.1 y 100.0", validators=[MaxValueValidator(100.0), MinValueValidator(0.1)], default=12
    )

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="registro")
    fecha_registro = models.DateTimeField(auto_now_add=True)
    tiempo_pago = models.DateTimeField(null=True, blank=True, verbose_name="Momento del pago")

    def __str__(self) -> str:
        return f"{self.nombre} de {self.nombres_tutor}"

    def get_absolute_url(self):
        return reverse(
            "registro:ver",
            args=[self.id],
        )


class ItemRegistro(models.Model):
    """Línea de detalle de un registro (productos/servicios añadidos)."""

    registro = models.ForeignKey(Registro, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Producto")
    servicio = models.ForeignKey(Servicio, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Servicio")
    descripcion = models.CharField(max_length=200, blank=True)
    cantidad = models.PositiveIntegerField(default=1)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo para la organización")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio público")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Item del registro"
        verbose_name_plural = "Items del registro"

    def __str__(self) -> str:
        if self.producto:
            return f"{self.producto.nombre} x {self.cantidad} - {self.registro.nombre}"
        elif self.servicio:
            return f"{self.servicio.nombre} - {self.registro.nombre}"
        else:
            return f"{self.descripcion} - {self.registro.nombre}"

    @property
    def total_price(self) -> Decimal:
        return self.cantidad * self.precio_unitario

    @property
    def total_cost(self) -> Decimal:
        return self.cantidad * self.costo_unitario
