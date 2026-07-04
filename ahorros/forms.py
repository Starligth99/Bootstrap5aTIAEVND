from django import forms

from .models import Deseo, Deuda, Gasto, GastoFijo, Ingreso, Nota, Recordatorio, PagoDeuda


class _BootstrapFormMixin:
    """Aplica clases de Bootstrap a los widgets del formulario."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            css = widget.attrs.get("class", "")
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = (css + " form-check-input").strip()
            elif isinstance(widget, forms.Select):
                widget.attrs["class"] = (css + " form-select").strip()
            else:
                widget.attrs["class"] = (css + " form-control").strip()
            if isinstance(widget, forms.DateInput):
                widget.input_type = "text"
                widget.attrs.setdefault("placeholder", "dd/mm/yyyy")
                widget.attrs.setdefault("inputmode", "numeric")
                widget.attrs.setdefault("pattern", r"\\d{2}/\\d{2}/\\d{4}")


class IngresoForm(_BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Ingreso
        fields = ["fecha", "monto", "fuente", "nota"]
        widgets = {
            "fecha": forms.DateInput(
                format="%d/%m/%Y",
                attrs={"placeholder": "dd/mm/yyyy", "inputmode": "numeric"},
            )
        }


class GastoForm(_BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ["fecha", "monto", "categoria", "descripcion", "evidencia"]
        widgets = {
            "fecha": forms.DateInput(
                format="%d/%m/%Y",
                attrs={"placeholder": "dd/mm/yyyy", "inputmode": "numeric"},
            )
        }


class GastoFijoForm(_BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = GastoFijo
        fields = ["nombre", "monto", "dia_pago", "activo", "nota", "evidencia"]


class DeudaForm(_BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Deuda
        fields = ["acreedor", "monto_original", "fecha", "plazo_meses", "nota", "evidencia"]
        widgets = {
            "fecha": forms.DateInput(
                format="%d/%m/%Y",
                attrs={"placeholder": "dd/mm/yyyy", "inputmode": "numeric"},
            )
        }


class PagoDeudaForm(_BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = PagoDeuda
        fields = ["fecha", "monto", "nota"]
        widgets = {
            "fecha": forms.DateInput(
                format="%d/%m/%Y",
                attrs={"placeholder": "dd/mm/yyyy", "inputmode": "numeric"},
            )
        }


class DeseoForm(_BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Deseo
        fields = ["nombre", "precio", "prioridad", "nota", "imagen"]


class NotaForm(_BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Nota
        fields = ["titulo", "contenido"]


class RecordatorioForm(_BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Recordatorio
        fields = ["titulo", "descripcion", "fecha_recordatorio"]
        widgets = {
            "fecha_recordatorio": forms.DateInput(
                format="%d/%m/%Y",
                attrs={"placeholder": "dd/mm/yyyy", "inputmode": "numeric"},
            )
        }
