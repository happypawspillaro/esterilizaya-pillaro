import logging

from campana.models import Campana, ItemCampana
from catalogo.models import ProductoBase
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

# Items por defecto a crear en cada campaña
ITEMS_DEFECTO = {
    "Servicio esterilizacion": {"costo": 8.5, "precio_publico": 15},
    "Analgesico 10Kg": {"costo": 0.8, "precio_publico": 1},
    "Analgesico 20Kg": {"costo": 1.0, "precio_publico": 1.25},
    "Analgesico Felino": {"costo": 3.5, "precio_publico": 3.8},
}


@receiver(post_save, sender=Campana)
def crear_items_campana(sender, instance, created, **kwargs):
    """
    Crea automáticamente los items de campaña por defecto
    cuando se crea una nueva campaña.
    """
    if created:
        for nombre_producto in ITEMS_DEFECTO.keys():
            try:
                # Obtener o crear el producto
                producto, _ = ProductoBase.objects.get_or_create(
                    nombre=nombre_producto,
                    defaults={
                        "costo": ITEMS_DEFECTO[nombre_producto]["costo"],
                        "precio_publico": ITEMS_DEFECTO[nombre_producto]["precio_publico"],
                    },
                )

                # Crear el item de campaña
                ItemCampana.objects.create(
                    campana=instance,
                    producto=producto,
                    costo=producto.costo,
                    precio_publico=producto.precio_publico,
                )

                logger.info(f"ItemCampana creado: {producto.nombre} para campaña {instance.nombre}")
            except Exception as e:
                logger.error(
                    f"Error al crear ItemCampana {nombre_producto} " f"para campaña {instance.nombre}: {str(e)}"
                )
