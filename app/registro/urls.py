from django.urls import path

from . import views

app_name = "registro"
urlpatterns = [
    path("", views.index, name="index"),
    path("lista/<int:campana_id>", views.lista, name="lista"),
    path("nuevo/<int:campana_id>/<int:inscripcion_id>", views.registrar, name="nuevo"),
    path("ver_ficha/<int:campana_id>/<int:registro_id>", views.ver_ficha, name="ver_ficha"),
    path("ver_certificados/<int:campana_id>", views.ver_certificados, name="ver_certificados"),
    path("ver_recetas/<int:campana_id>", views.ver_recetas, name="ver_recetas"),
    path("vista_veterinarios/<int:campana_id>", views.RegistradoListView.as_view(), name="vista_veterinarios"),
    path("registro/<int:registro_id>/generar_pdf/", views.generar_pdf, name="generar_pdf"),
    path("razas/", views.obtener_razas, name="razas"),
    path("barrios/", views.obtener_barrios, name="barrios"),
    path(
        "ver/<int:id>",
        views.ver_mascota,
        name="ver",
    ),
    path("carrito/<int:registro_id>/", views.vista_carrito, name="carrito"),
    path(
        "carrito/<int:registro_id>/actualizar_esterilizacion/",
        views.htmx_actualizar_esterilizacion,
        name="htmx_actualizar_esterilizacion",
    ),
    path(
        "carrito/<int:registro_id>/actualizar_cantidad/<int:item_id>/",
        views.htmx_actualizar_cantidad,
        name="htmx_actualizar_cantidad",
    ),
    path("carrito/<int:registro_id>/anadir_item/", views.htmx_anadir_item, name="htmx_anadir_item"),
    path("carrito/<int:registro_id>/remover_item/<int:item_id>/", views.htmx_remover_item, name="htmx_remover_item"),
    path("carrito/<int:registro_id>/total/", views.htmx_total_carrito, name="htmx_total_carrito"),
    path("confirmar/<int:registro_id>/", views.confirmar_pago, name="confirmar_pago"),
]
