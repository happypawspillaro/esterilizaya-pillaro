# campana/reportes.py (fragmento final modificado)
import logging
from decimal import Decimal

from django.db.models import DecimalField, F, Sum, Value
from django.db.models.functions import Coalesce
from pago.models import Pago, PagoExtra, PagoOtro, PagoProducto, PagoServicio

from .models import Campana

logger = logging.getLogger(__name__)


def reporte_financiero(campana_id: int) -> dict:
    campana = Campana.objects.get(id=campana_id)

    servicios = PagoServicio.objects.filter(pago__registro__inscripcion__campana=campana)
    productos = PagoProducto.objects.filter(pago__registro__inscripcion__campana=campana)
    extras = PagoExtra.objects.filter(pago__registro__inscripcion__campana=campana)
    otros = PagoOtro.objects.filter(pago__registro__inscripcion__campana=campana)
    pagos = Pago.objects.filter(registro__inscripcion__campana=campana)

    # --- Totales de pagos (para referencia, pero no se usan en la vista principal ahora) ---
    total_pagos_efectivo = pagos.filter(metodo="EFE").aggregate(
        total=Coalesce(Sum("monto_total"), Value(0, output_field=DecimalField()))
    )["total"]
    total_pagos_transferencia = pagos.filter(metodo="TRAN").aggregate(
        total=Coalesce(Sum("monto_total"), Value(0, output_field=DecimalField()))
    )["total"]
    total_pagos_otro = pagos.filter(metodo="OTRO").aggregate(
        total=Coalesce(Sum("monto_total"), Value(0, output_field=DecimalField()))
    )["total"]
    total_pagos = pagos.aggregate(total=Coalesce(Sum("monto_total"), Value(0, output_field=DecimalField())))["total"]

    # --- COSTOS ---
    # Servicios: costo_veterinario es el costo
    total_costo_servicios = servicios.aggregate(
        total=Coalesce(Sum("costo_veterinario"), Value(0, output_field=DecimalField()))
    )["total"]
    cantidad_servicios = servicios.count()

    # Productos: costo_unitario * cantidad
    total_costo_productos = productos.aggregate(
        total=Coalesce(
            Sum(F("costo_unitario") * F("cantidad"), output_field=DecimalField()), Value(0, output_field=DecimalField())
        )
    )["total"]
    cantidad_productos = productos.count()

    # Extras: el precio del extra es el costo (no hay margen)
    total_costo_extras = extras.aggregate(total=Coalesce(Sum("precio"), Value(0, output_field=DecimalField())))["total"]
    extras_detalle = list(extras.values("descripcion", "precio"))

    # Detalle de productos para costos (opcional, pero podemos mostrarlo si se quiere)
    costo_productos_detalle = []
    for p in (
        productos.values("nombre_producto")
        .annotate(
            cantidad_total=Sum("cantidad"),
            costo_total=Sum(F("costo_unitario") * F("cantidad"), output_field=DecimalField()),
        )
        .order_by("nombre_producto")
    ):
        costo_productos_detalle.append(
            {
                "nombre": p["nombre_producto"],
                "cantidad": p["cantidad_total"],
                "costo_total": p["costo_total"],
            }
        )

    # --- INGRESOS ---
    # Servicios: precio al público
    total_ingreso_servicios = servicios.aggregate(total=Coalesce(Sum("precio"), Value(0, output_field=DecimalField())))[
        "total"
    ]

    # Productos: precio_unitario * cantidad
    total_ingreso_productos = productos.aggregate(
        total=Coalesce(
            Sum(F("precio_unitario") * F("cantidad"), output_field=DecimalField()),
            Value(0, output_field=DecimalField()),
        )
    )["total"]

    # Extras: precio (ingreso)
    total_ingreso_extras = extras.aggregate(total=Coalesce(Sum("precio"), Value(0, output_field=DecimalField())))[
        "total"
    ]

    # Otros: precio
    total_ingreso_otros = otros.aggregate(total=Coalesce(Sum("precio"), Value(0, output_field=DecimalField())))["total"]
    otros_detalle = list(otros.values("descripcion", "precio"))

    # Detalle de productos para ingresos
    ingreso_productos_detalle = []
    for p in (
        productos.values("nombre_producto")
        .annotate(
            cantidad_total=Sum("cantidad"),
            ingreso_total=Sum(F("precio_unitario") * F("cantidad"), output_field=DecimalField()),
        )
        .order_by("nombre_producto")
    ):
        ingreso_productos_detalle.append(
            {
                "nombre": p["nombre_producto"],
                "cantidad": p["cantidad_total"],
                "ingreso_total": p["ingreso_total"],
            }
        )

    return {
        "campana": campana,
        "costos": {
            "servicios": {
                "total": total_costo_servicios,
                "cantidad": cantidad_servicios,
            },
            "productos": {
                "total": total_costo_productos,
                "cantidad": cantidad_productos,
                "detalle": costo_productos_detalle,  # lista con nombre, cantidad, costo_total
            },
            "extras": {
                "total": total_costo_extras,
                "detalle": extras_detalle,
            },
            "total": total_costo_servicios + total_costo_productos + total_costo_extras,
        },
        "ingresos": {
            "servicios": {
                "total": total_ingreso_servicios,
                "cantidad": cantidad_servicios,
            },
            "productos": {
                "total": total_ingreso_productos,
                "cantidad": cantidad_productos,
                "detalle": ingreso_productos_detalle,
            },
            "extras": {
                "total": total_ingreso_extras,
                "cantidad": extras.count(),
            },
            "otros": {
                "total": total_ingreso_otros,
                "detalle": otros_detalle,
            },
            "total": total_ingreso_servicios + total_ingreso_productos + total_ingreso_extras + total_ingreso_otros,
        },
        "pagos": {
            "efectivo": total_pagos_efectivo,
            "transferencia": total_pagos_transferencia,
            "otro": total_pagos_otro,
            "total": total_pagos,
        },
    }
