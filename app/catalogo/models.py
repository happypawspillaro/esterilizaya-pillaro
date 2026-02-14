from django.db import models


class ProductoBase(models.Model):
    """
    El  'Menú' de servicios o medicinas.
    Por ejemplo: Costo interno: 'Carprofen 25(10kg)', Costo Público: 'Carprofen 25'
    """

    class Meta:
        verbose_name = "Producto/Servicio"
        verbose_name_plural = "Productos y Servicios"

    nombre = models.CharField(max_length=100, unique=True)

    # Estos son los precios 'sugeridos' que se copiarán a la campaña
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    precio_publico = models.DecimalField(max_digits=10, decimal_places=2)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre}"
