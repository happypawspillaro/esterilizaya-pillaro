import logging

from campana.models import ProductoCampana
from django import forms

from .models import Registro

logger = logging.getLogger(__name__)


class RegistroForm(forms.ModelForm):
    peso = forms.FloatField(widget=forms.NumberInput(attrs={"step": "0.1", "min": "0"}))

    class Meta:
        model = Registro
        exclude = ["inscripcion", "usuario", "tiempo_pago"]

    def __init__(self, *args, **kwargs):
        self.inscripcion_campana_id = kwargs.pop("inscripcion_campana_id", None)
        super().__init__(*args, **kwargs)
        self.fields["raza_mascota"].widget.attrs.update(
            {
                "class": "form-control autocomplete",
                "autocomplete": "on",
                "placeholder": "Escribe para buscar razas registradas...",
                "data-suggestions-threshold": "1",
            }
        )

    def clean_numero_turno(self):
        numero_turno = self.cleaned_data.get("numero_turno")
        if Registro.objects.filter(
            numero_turno=numero_turno, inscripcion__campana__id=self.inscripcion_campana_id
        ).exists():
            raise forms.ValidationError(
                f"El turno {numero_turno} ya ha sido asignado a otro tutor, agregue el turno correcto."
            )
        return numero_turno


class AnadirMedicinaForma(forms.Form):
    producto_campana = forms.ModelChoiceField(
        queryset=ProductoCampana.objects.none(),
        label="Medicina",
        empty_label="Seleccione una medicina",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    cantidad = forms.IntegerField(
        label="Cantidad",
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={"class": "form-control", "style": "width: 80px;"}),
    )

    def __init__(self, campana, especie, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["producto_campana"].queryset = ProductoCampana.objects.filter(
            campana=campana,
        ).select_related("producto")
        if especie == "🐕":
            self.fields["cantidad"].initial = 4
        elif especie == "🐈":
            self.fields["cantidad"].initial = 1


class AnadirFormaExtraVeterinario(forms.Form):
    descripcion = forms.CharField(
        max_length=200, label="Descripción", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    precio = forms.DecimalField(
        max_digits=10, decimal_places=2, label="Precio", widget=forms.NumberInput(attrs={"class": "form-control"})
    )


class FormaOtroOrganizacion(forms.Form):
    descripcion = forms.CharField(
        max_length=200, label="Descripción", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    precio = forms.DecimalField(
        max_digits=10, decimal_places=2, label="Precio", widget=forms.NumberInput(attrs={"class": "form-control"})
    )
