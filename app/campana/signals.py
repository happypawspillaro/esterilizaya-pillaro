import logging

from campana.models import Campana, Producto, ProductoCampana, Servicio, ServicioCampana
from django.db.models.signals import post_save
from django.dispatch import receiver
from esterilizaya.constantes import ITEMS_DEFECTO

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Campana)
def crear_items_campana(sender, instance, created, **kwargs):
    """
    Crea automáticamente los items de campaña por defecto
    cuando se crea una nueva campaña.
    """
    if created:
        for p_key in ITEMS_DEFECTO.keys():
            for prod_data in ITEMS_DEFECTO[p_key]:
                try:
                    if p_key == "SERVICIOS":

                        servicio, creado = Servicio.objects.get_or_create(
                            nombre=prod_data["nombre"],
                            defaults={
                                "descripcion": prod_data["descripcion"],
                                "categoria": prod_data["categoria"],
                                "default_costo_veterinario": prod_data["default_costo_veterinario"],
                                "default_precio_publico": prod_data["default_precio_publico"],
                            },
                        )
                        logger.info(f"Servicio creado: {creado}?: {servicio}")

                        if creado:
                            logger.info(f"Asociando producto {servicio.nombre} a Campaña {instance.nombre}")
                            ServicioCampana.objects.get_or_create(
                                campana=instance,
                                servicio=servicio,
                                defaults={
                                    "costo_veterinario": servicio.default_costo_veterinario,
                                    "precio_publico": servicio.default_precio_publico,
                                },
                            )
                    elif p_key == "PRODUCTOS":
                        logger.info(prod_data)
                        producto, creado = Producto.objects.get_or_create(
                            nombre=prod_data["nombre"],
                            defaults={
                                "descripcion": prod_data["descripcion"],
                                "especie_objetivo": prod_data.get("especie_objetivo"),
                                "tipo_medicina": prod_data.get("tipo_medicina", "ANA"),
                                "peso_recomendado": prod_data.get("peso_recomendado", 0),
                                "default_precio_compra": prod_data["default_precio_compra"],
                                "default_precio_venta": prod_data["default_precio_venta"],
                            },
                        )
                        logger.info(f"Producto creado: {creado}?, {producto}")
                        if creado:
                            logger.info(f"Asociando producto {producto.nombre} a Campaña {instance.nombre}")
                            ProductoCampana.objects.get_or_create(
                                campana=instance,
                                producto=producto,
                                defaults={
                                    "precio_compra": producto.default_precio_compra,
                                    "precio_venta": producto.default_precio_venta,
                                },
                            )
                    logger.info(f"ItemCampana creado: {prod_data['nombre']} para campaña {instance.nombre}")
                except Exception as e:
                    logger.error(f"Error al crear ItemCampana {prod_data} " f"para campaña {instance.nombre}: {str(e)}")
