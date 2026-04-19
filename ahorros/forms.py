from django import forms

from .models import Deuda, Gasto, GastoFijo, Ingreso, PagoDeuda


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
                widget.input_type = "date"


class IngresoForm(_BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Ingreso
        fields = ["fecha", "monto", "fuente", "nota"]
        widgets = {"fecha": forms.DateInput()}


class GastoForm(_BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ["fecha", "monto", "categoria", "descripcion"]
        widgets = {"fecha": forms.DateInput()}


class GastoFijoForm(_BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = GastoFijo
        fields = ["nombre", "monto", "dia_pago", "activo", "nota"]


class DeudaForm(_BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Deuda
        fields = ["acreedor", "monto_original", "fecha", "nota"]
        widgets = {"fecha": forms.DateInput()}


class PagoDeudaForm(_BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = PagoDeuda
        fields = ["fecha", "monto", "nota"]
        widgets = {"fecha": forms.DateInput()}
