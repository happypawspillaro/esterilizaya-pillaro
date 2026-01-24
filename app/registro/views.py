import json
import logging

from campana.models import Campana
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.core.paginator import Paginator
from django.http import JsonResponse, response
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.generic import ListView
from easy_thumbnails.files import get_thumbnailer
from esterilizaya.constantes import RUTA_PDFS
from inscripcion.models import Inscripcion
from registro.models import Registro
from weasyprint import HTML

from .forms import RegistroForm

logger = logging.getLogger(__name__)


def index(request):
    campanas = Campana.objects.all()

    return render(request, "registro/index.html", {"campanas": campanas})


def lista(request, campana_id):
    page_number = request.GET.get("page", 1)
    todos_registros = Registro.objects.filter(inscripcion__campana=campana_id)
    # Dato del primer resultado
    campana = Campana.objects.filter(id=campana_id).first()
    if not campana:
        logger.warning("No existe la campaña seleccionada, abortando...")
        messages.error(request, "¡No existe la campaña seleccionada, regresando al inicio!")
        return redirect("inicio:index")
    query = ""
    if "query" in request.GET:
        query = request.GET["query"]
    if query:
        todos_registros = todos_registros.filter(nombres_tutor__iregex=query)
    # Paginación
    paginator = Paginator(todos_registros, 15)
    registros = paginator.get_page(page_number)
    breadcrumbs = [
        {"titulo": campana.nombre, "url": campana.get_absolute_url()},
        {"titulo": "Todos Registros", "url": None},
    ]
    return render(
        request,
        "registro/lista.html",
        {"registros": registros, "campana": campana, "breadcrumbs": breadcrumbs},
    )


@login_required(login_url="cuenta:login")
def registrar(request, campana_id, inscripcion_id):
    inscripcion = get_object_or_404(Inscripcion, id=inscripcion_id, campana_id=campana_id)
    # Chequear si hay cupos disponibles
    if inscripcion.cupos_registrados >= inscripcion.cupos_totales:
        messages.error(
            request,
            f"Lo siento, ya no hay más cupos disponibles para {inscripcion.nombres_tutor}",
        )
        return redirect("inscripcion:index", campana_id=inscripcion.campana.id)
    breadcrumbs = []
    if request.method == "POST":
        forma = RegistroForm(request.POST, request.FILES, inscripcion_campana_id=campana_id)
        if forma.is_valid():
            registro_forma = forma.save(commit=False)
            usuario = User.objects.get(username=request.user)
            registro_forma.inscripcion = inscripcion
            registro_forma.usuario = usuario
            inscripcion.cupos_registrados += 1
            inscripcion.save()
            registro_forma.save()
            registro_id = registro_forma.id
            return redirect("registro:ver_ficha", campana_id=campana_id, registro_id=registro_id)
        else:
            forma.clean()
    else:
        registro_anterior = (
            Registro.objects.filter(
                inscripcion__campana_id=campana_id,
                inscripcion__nombres_tutor=inscripcion.nombres_tutor,
            )
            .order_by("-id")
            .first()
        )
        initial_data = {}
        if registro_anterior:
            initial_data = {
                "cedula_identidad": registro_anterior.cedula_identidad,
                "n_animales_hogar": registro_anterior.n_animales_hogar,
                "n_animales_hogar_esterilizadas": registro_anterior.n_animales_hogar_esterilizadas,
            }
        forma = RegistroForm(
            instance=inscripcion,
            inscripcion_campana_id=campana_id,
            initial=initial_data,
        )
        breadcrumbs = [
            {
                "titulo": inscripcion.campana.nombre,
                "url": inscripcion.campana.get_absolute_url(),
            },
            {"titulo": "Registro", "url": None},
        ]
    return render(request, "registro/nuevo.html", {"form": forma, "breadcrumbs": breadcrumbs})


@login_required(login_url="cuenta:login")
def ver_ficha(request, campana_id, registro_id):
    registro = get_object_or_404(Registro, id=registro_id, inscripcion__campana=campana_id)
    return render(request, "registro/ficha.html", {"registro": registro})


# TODO: Simplificar todos los registros
def ver_certificados(request, campana_id):
    registros = Registro.objects.filter(inscripcion__campana=campana_id)
    return render(
        request,
        "registro/certificados/hoja_certificados.html",
        {"registros": registros},
    )


def ver_recetas(request, campana_id):
    registros = Registro.objects.filter(inscripcion__campana=campana_id)
    return render(request, "registro/recetas/hoja_recetas.html", {"registros": registros})


class RegistradoListView(ListView):
    model = Registro
    template_name = "registro/vista_veterinarios.html"
    context_object_name = "registros"

    def get_queryset(self):
        """
        Filters pets by the given campaign_id.
        """
        campana_id = self.kwargs.get("campana_id")  # Retrieve campaign_id from URL kwargs
        return Registro.objects.filter(inscripcion__campana=campana_id)  # Filter pets for the given campaign

    def get(self, request, *args, **kwargs):
        """
        Handles AJAX requests to dynamically update the table.
        """
        campana_id = self.kwargs.get("campana_id")
        if request.headers.get("x-requested-with") == "XMLHttpRequest":  # Check for Ajax requests
            registros = list(
                Registro.objects.filter(inscripcion__campana=campana_id).values(
                    "foto",
                    "especie",
                    "peso",
                    "nombre",
                    "vulnerable",
                    "sexo",
                    "edad_anos",
                    "edad_meses",
                    "fecha_registro",
                    "observaciones",
                    "numero_turno",
                    "nombres_tutor",
                )
            )
            # Añadir ruta del miniatura
            for reg in registros:
                reg["miniatura"] = (
                    get_thumbnailer(reg["foto"]).get_thumbnail({"size": (300, 300), "crop": "smart"}).url
                    if reg["foto"]
                    else ""
                )
            return JsonResponse({"registros": registros})
        return super().get(request, *args, **kwargs)


@login_required(login_url="cuenta:login")
def generar_pdf(request, registro_id):
    # TODO: Eliminar esto cuando el SSL sea global
    import ssl

    ssl._create_default_https_context = ssl._create_unverified_context
    registro = get_object_or_404(Registro, id=registro_id)
    html_string = render_to_string("registro/ficha.html", {"registro": registro, "pdf_mode": True})
    if not RUTA_PDFS.exists():
        RUTA_PDFS.mkdir(parents=True, exist_ok=True)
    ruta_ficha_pdf = RUTA_PDFS / f"ficha_{registro.numero_turno}_{registro.nombre}_{registro_id}.pdf"
    try:
        extra_html = {}
        extra_css = {}
        if settings.DEBUG:
            extra_css["stylesheets"] = [finders.find("css/bootstrap.min.css")]
            extra_html["base_url"] = request.build_absolute_uri()
        else:
            extra_html["base_url"] = "https://nginx"
        HTML(string=html_string, **extra_html).write_pdf(ruta_ficha_pdf, **extra_css)
        logger.info(f"PDF guardado en: {ruta_ficha_pdf}")
        messages.success(request, "PDF generado y guardado exitosamente.")
    except Exception as e:
        logger.error(f"Error al guardar el PDF: {e}")
        messages.error(request, "Error al generar el PDF. Por favor, inténtelo de nuevo más tarde.")
        return redirect(
            "registro:ver_ficha",
            campana_id=registro.inscripcion.campana.id,
            registro_id=registro_id,
        )
    return redirect("registro:lista", campana_id=registro.inscripcion.campana.id)


def obtener_razas(request):
    query = request.GET.get("term", "")
    # Obtener razas únicas de registros en campañas pasadas y que sus nombres hayan sido corregidos
    # para que coincidan con la consulta via AJAX
    raza_mascota = (
        Registro.objects.filter(
            raza_mascota__icontains=query,
            inscripcion__campana__estado=Campana.Estado.PASADA,
        )
        .order_by("raza_mascota")
        .values_list("raza_mascota", flat=True)
        .distinct()
    )
    return JsonResponse(list(raza_mascota), safe=False)


def obtener_barrios(request):
    query = request.GET.get("term", "").lower()
    canton = request.GET.get("canton", "")
    parroquia = request.GET.get("parroquia", "")

    # Intentar múltiples ocasiones para encontrar el archivo
    ruta_locaciones = finders.find("assets/locaciones.json")
    if not ruta_locaciones:
        # Intento a la ruta directa si finders.find falla en encontrarlo
        ruta_locaciones = settings.BASE_DIR / "static" / "assets" / "locaciones.json"

    try:
        with open(ruta_locaciones, "r", encoding="utf-8") as f:
            locaciones = json.load(f)

        barrios = []
        # Filtrar por cantón y parroquia si se proporcionan
        if canton and parroquia:
            if canton in locaciones and parroquia in locaciones[canton]:
                barrios_dict = locaciones[canton][parroquia]
                barrios = [barrio for barrio in barrios_dict.keys() if query in barrio.lower()]
                barrios.sort()

        return JsonResponse(barrios, safe=False)
    except Exception as e:
        logger.error(f"Error al cargar locaciones {ruta_locaciones}: {e}")
        return JsonResponse([], safe=False)


def ver_mascota(request, id):
    try:
        registro = get_object_or_404(Registro, id=id)
    except response.Http404:
        messages.error(request, f"Error, el registro {id} no existe")
        return redirect("mascotas:index")
    return render(request, "mascota.html", {"registro": registro})
