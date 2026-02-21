# campana/reportes.py (fragmento final modificado)
import logging

from campana.models import Campana, ProductoCampana
from django.db.models import DecimalField, F, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from pago.models import Pago, PagoExtra, PagoOtro, PagoProducto, PagoServicio
from registro.models import Registro

logger = logging.getLogger(__name__)


def devolver_extras(campana: Campana):
    servicios = PagoServicio.objects.filter(pago__registro__inscripcion__campana=campana)
    productos = PagoProducto.objects.filter(pago__registro__inscripcion__campana=campana)
    extras = PagoExtra.objects.filter(pago__registro__inscripcion__campana=campana)
    otros = PagoOtro.objects.filter(pago__registro__inscripcion__campana=campana)
    pagos = Pago.objects.filter(registro__inscripcion__campana=campana)
    return servicios, productos, extras, otros, pagos


def reporte_financiero(campana_id: int) -> dict:
    campana = Campana.objects.get(id=campana_id)
    servicios, productos, extras, otros, pagos = devolver_extras(campana)

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


def financiero_detallado(campana_id: int):
    campana = get_object_or_404(Campana, id=campana_id)

    registros = (
        Registro.objects.filter(inscripcion__campana=campana, tiempo_pago__isnull=False)
        .select_related("pago")
        .prefetch_related(
            "pago__servicios",
            "pago__productos",
            "pago__extras",
            "pago__otros",
        )
        .order_by("numero_turno")
    )

    # Productos activos en la campaña
    productos_unicos = list(
        ProductoCampana.objects.filter(campana=campana, esta_activo=True)
        .values_list("producto__nombre", flat=True)
        .distinct()
        .order_by("producto__nombre")
    )

    data_registros = []

    for reg in registros:
        pago = getattr(reg, "pago", None)

        # Inicializar mapa de productos
        productos_dict = {nombre: None for nombre in productos_unicos}

        if pago:
            # Servicios
            servicio_total = sum(s.precio for s in pago.servicios.all())

            # Productos
            for prod in pago.productos.all():
                nombre = prod.nombre_producto
                productos_dict[nombre] = prod.cantidad

            # Extras
            extras = list(pago.extras.all())
            otros = list(pago.otros.all())

            extra_data = (
                {
                    "descripcion": e.descripcion,
                    "costo": e.precio,
                }
                for e in extras
            )

            otro_data = (
                {
                    "descripcion": o.descripcion,
                    "costo": o.precio,
                }
                for o in otros
            )

            reg_data = {
                "numero_turno": reg.numero_turno,
                "nombres_tutor": reg.nombres_tutor,
                "nombre": reg.nombre,
                "observaciones": reg.observaciones,
                "especie": reg.get_especie_display(),
                "genero": reg.get_sexo_display(),
                "peso": reg.peso,
                "vulnerable": reg.vulnerable,
                "barrio": reg.barrio_tutor,
                "parroquia": reg.get_parroquia_tutor_display(),
                "pago": {
                    "servicio": servicio_total,
                    "productos": productos_dict,
                    "extras": list(extra_data),
                    "otros": list(otro_data),
                    "total": pago.monto_total,
                    "metodo": pago.get_metodo_display(),
                    "nota": pago.notas,
                    "usuario": pago.usuario
                },
            }

            data_registros.append(reg_data)
    total_general = sum(r["pago"]["total"] for r in data_registros if r.get("pago"))
    return {
        "registros": data_registros,
        "items": productos_unicos,
        "campana": campana,
        "total_general": total_general,
    }
