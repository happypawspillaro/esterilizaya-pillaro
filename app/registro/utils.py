import logging
from decimal import Decimal

from campana.models import Campana, ProductoCampana, Servicio, ServicioCampana

logger = logging.getLogger(__name__)


def calcular_precio_sugerido_esterilizacion(campana, peso, vulnerable=False) -> Decimal:
    """
    Calcula el precio sugerido para el servicio de esterilización.
    - Si vulnerable: gratis (0).
    - Precio base: precio_publico del servicio en la campaña.
    - Sobrecosto cada 5kg por encima de 15kg: $2 por cada 5kg adicionales.
    """
    if vulnerable:
        return Decimal("0.00")

    try:
        servicio_ester = Servicio.objects.get(categoria="EST")
        servicio_campana = ServicioCampana.objects.get(campana=campana, servicio=servicio_ester)
        precio_base = servicio_campana.precio_publico
    except (Servicio.DoesNotExist, ServicioCampana.DoesNotExist) as e:
        logger.warning(
            "No se encontró el servicio de esterilización en la campaña. Usando precio base por defecto de $15.00."
            f"Razón: {e}"
        )
        precio_base = Decimal(
            "15.00"
        )  # Pon los 15 en caso de que no se encuentre el servicio o la asociación en la campaña

    if peso and peso > 15:
        extra_kg = peso - 15
        extra_unidades = extra_kg // 5
        precio_base += Decimal(extra_unidades * 2)

    return precio_base


def sugerir_medicamento(campana: Campana, especie: str, peso: float) -> ProductoCampana:
    """
    Sugiere un medicamento (analgésico) según especie y peso.
    Busca en los productos activos de la campaña que coincidan con:
    - especie: son diferentes los analgésicos para perros y gatos
    - peso: el analgésico recomendado varía según el peso del animal (para perros)
    Retorna el primer ProductoCampana que cumpla o None.
    """
    if especie not in ["🐕", "🐈"]:
        return None

    qs = ProductoCampana.objects.filter(
        campana=campana, producto__especie_objetivo=especie, producto__tipo_medicina="ANA"
    ).select_related("producto")
    if peso is not None:
        if especie == "🐕":
            if peso <= 10:
                qs = qs.filter(producto__peso_recomendado__lte=10)
            elif 10 < peso <= 30:
                qs = qs.filter(producto__peso_recomendado__gt=10, producto__peso_recomendado__lte=20)
            else:
                logger.warning(f"Peso {peso} excede rango recomendado para perros. No se sugiere medicamento.")
                return None
    return qs.first()
