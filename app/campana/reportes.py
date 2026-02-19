from decimal import Decimal

from django.db.models import F, Sum, Value
from django.db.models.functions import Coalesce
from pago.models import PagoExtra, PagoOtro, PagoProducto, PagoServicio

from .models import Campana


def reporte_financiero(campana_id: int) -> dict:
    """Genera un reporte financiero para una campaña usando los snapshots específicos."""
    campana = Campana.objects.get(id=campana_id)

    # Totales por tipo
    servicios = PagoServicio.objects.filter(pago__registro__inscripcion__campana=campana)
    productos = PagoProducto.objects.filter(pago__registro__inscripcion__campana=campana)
    extras = PagoExtra.objects.filter(pago__registro__inscripcion__campana=campana)
    otros = PagoOtro.objects.filter(pago__registro__inscripcion__campana=campana)

    total_costo = (
        servicios.aggregate(total=Coalesce(Sum("costo_veterinario"), Value(0)))["total"]
        + productos.aggregate(total=Coalesce(Sum(F("costo_unitario") * F("cantidad")), Value(0)))["total"]
        +
        # extras y otros no tienen costo (por ahora), así que sumamos 0
        Decimal(0)
    )

    total_ingreso = (
        servicios.aggregate(total=Coalesce(Sum("precio"), Value(0)))["total"]
        + productos.aggregate(total=Coalesce(Sum(F("precio_unitario") * F("cantidad")), Value(0)))["total"]
        + extras.aggregate(total=Coalesce(Sum("precio"), Value(0)))["total"]
        + otros.aggregate(total=Coalesce(Sum("precio"), Value(0)))["total"]
    )

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
