from django.urls import path

from . import views

app_name = "campana"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:anio>/<str:parroquia>/<int:mes>/<int:dia>/", views.mostrar, name="mostrar"),
    path("listar_canton_parroquia/", views.listar_canton_parroquia, name="listar_canton_parroquia"),
    path("reporte/<int:campana_id>/", views.reporte_financiero_resumen, name="reporte_financiero_resumen"),
    path("reporte/<int:campana_id>/detallado", views.reporte_financiero_detallado, name="reporte_financiero_detallado"),
]
