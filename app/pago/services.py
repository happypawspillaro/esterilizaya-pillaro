from decimal import Decimal

from django.utils import timezone
from registro.models import Registro

from .models import Pago, PagoExtra, PagoOtro, PagoProducto, PagoServicio


def registrar_pago(
    registro: Registro, monto_total: Decimal, metodo: str = "efectivo", notas: str = "", usuario=None
) -> Pago:
    """
    Registra un pago para una registración, creando los detalles específicos según el tipo de item.
    """
    pago = Pago.objects.create(registro=registro, monto_total=monto_total, metodo=metodo, notas=notas, usuario=usuario)

    for item in registro.items.all():
        if item.servicio:
            # Servicio (esterilización u otro servicio)
            PagoServicio.objects.create(
                pago=pago,
                servicio=item.servicio,
                nombre_servicio=item.servicio.nombre,
                descripcion=item.descripcion,
                precio=item.precio_unitario,
                costo_veterinario=item.costo_unitario,
            )
        elif item.producto:
            # Producto (medicina)
            PagoProducto.objects.create(
                pago=pago,
                producto=item.producto,
                nombre_producto=item.producto.nombre,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario,
                costo_unitario=item.costo_unitario,
            )
        elif "[Extra]" in item.descripcion:
            # Extra veterinario (solo precio)
            PagoExtra.objects.create(
                pago=pago, descripcion=item.descripcion.replace("[Extra] ", ""), precio=item.precio_unitario
            )
        elif "[Otro]" in item.descripcion:
            # Otro (solo precio)
            PagoOtro.objects.create(
                pago=pago, descripcion=item.descripcion.replace("[Otro] ", ""), precio=item.precio_unitario
            )
        else:
            # Fallback: si no coincide, lo guardamos como otro
            PagoOtro.objects.create(
                pago=pago, descripcion=item.descripcion or "Item sin clasificar", precio=item.precio_unitario
            )

    registro.tiempo_pago = timezone.now()
    registro.save()
    return pago
