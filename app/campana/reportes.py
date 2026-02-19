import logging
from decimal import Decimal

from django.db.models import DecimalField, F, Sum, Value
from django.db.models.functions import Coalesce
from pago.models import PagoExtra, PagoOtro, PagoProducto, PagoServicio

from .models import Campana

logger = logging.getLogger(__name__)


def reporte_financiero(campana_id: int) -> dict:
    """Genera un reporte financiero para una campaña usando los snapshots específicos."""
    campana = Campana.objects.get(id=campana_id)

    # Totales por tipo
    servicios = PagoServicio.objects.filter(pago__registro__inscripcion__campana=campana)
    productos = PagoProducto.objects.filter(pago__registro__inscripcion__campana=campana)
    extras = PagoExtra.objects.filter(pago__registro__inscripcion__campana=campana)
    otros = PagoOtro.objects.filter(pago__registro__inscripcion__campana=campana)
    logger.debug(f"Servicios encontrados: {servicios.count()}")
    logger.debug(f"Productos encontrados: {productos.count()}")
    logger.debug(f"Extras encontrados: {extras.count()}")
    logger.debug(f"Otros encontrados: {otros.count()}")
    # Cálculo del total de costos
    total_costo_servicios = servicios.aggregate(
        total=Coalesce(Sum("costo_veterinario"), Value(0, output_field=DecimalField()))
    )["total"]
    total_costo_productos = productos.aggregate(
        total=Coalesce(
            Sum(F("costo_unitario") * F("cantidad"), output_field=DecimalField()), Value(0, output_field=DecimalField())
        )
    )["total"]
    total_costo = total_costo_servicios + total_costo_productos + Decimal(0)
    # Cálculo del total de ingresos
    total_ingresos_servicios = servicios.aggregate(
        total=Coalesce(Sum("precio"), Value(0, output_field=DecimalField()))
    )["total"]
    total_ingresos_productos = productos.aggregate(
        total=Coalesce(
            Sum(F("precio_unitario") * F("cantidad"), output_field=DecimalField()),
            Value(0, output_field=DecimalField()),
        )
    )["total"]
    total_ingresos_extras = extras.aggregate(total=Coalesce(Sum("precio"), Value(0, output_field=DecimalField())))[
        "total"
    ]
    total_ingresos_otros = otros.aggregate(total=Coalesce(Sum("precio"), Value(0, output_field=DecimalField())))[
        "total"
    ]
    total_ingreso = total_ingresos_servicios + total_ingresos_productos + total_ingresos_extras + total_ingresos_otros

    # Detalle combinado
    detalle = []

    for s in servicios:
        detalle.append(
            {
                "tipo": "Servicio",
                "descripcion": s.nombre_servicio or str(s.servicio),
                "cantidad": 1,
                "costo_total": s.costo_veterinario,
                "ingreso_total": s.precio,
            }
        )

    for p in productos:
        detalle.append(
            {
                "tipo": "Producto",
                "descripcion": p.nombre_producto,
                "cantidad": p.cantidad,
                "costo_total": p.costo_unitario * p.cantidad,
                "ingreso_total": p.precio_unitario * p.cantidad,
            }
        )

    for e in extras:
        detalle.append(
            {
                "tipo": "Extra",
                "descripcion": e.descripcion,
                "cantidad": 1,
                "costo_total": 0,
                "ingreso_total": e.precio,
            }
        )

    for o in otros:
        detalle.append(
            {
                "tipo": "Otro",
                "descripcion": o.descripcion,
                "cantidad": 1,
                "costo_total": 0,
                "ingreso_total": o.precio,
            }
        )

    return {
        "campana": campana,
        "total_costo": total_costo,
        "total_ingreso": total_ingreso,
        "ganancia": total_ingreso - total_costo,
        "detalle": detalle,
    }
