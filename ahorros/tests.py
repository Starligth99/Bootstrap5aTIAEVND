from django.test import TestCase
from django.urls import reverse

from .forms import DeudaForm, DeseoForm, GastoFijoForm, GastoForm, IngresoForm


class FormValidationTests(TestCase):
    def test_gasto_form_allows_saving_without_evidence(self):
        form = GastoForm(
            data={
                "fecha": "2026-06-26",
                "monto": "10.50",
                "categoria": "otro",
                "descripcion": "Prueba",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_deuda_form_allows_saving_without_evidence(self):
        form = DeudaForm(
            data={
                "acreedor": "Juan",
                "monto_original": "100.00",
                "fecha": "2026-06-26",
                "plazo_meses": "3",
                "nota": "Prueba",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_deseo_form_allows_saving_without_image(self):
        form = DeseoForm(
            data={
                "nombre": "Laptop",
                "precio": "500.00",
                "prioridad": "alta",
                "nota": "Prueba",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_gasto_fijo_form_allows_saving_without_evidence(self):
        form = GastoFijoForm(
            data={
                "nombre": "Internet",
                "monto": "40.00",
                "dia_pago": "15",
                "activo": True,
                "nota": "Prueba",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_ingreso_form_accepts_day_month_year_dates(self):
        form = IngresoForm(
            data={
                "fecha": "27/06/2026",
                "monto": "10.50",
                "fuente": "Prueba",
                "nota": "Prueba",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_date_inputs_render_with_text_widget_for_manual_entry(self):
        form = IngresoForm()
        self.assertEqual(form.fields["fecha"].widget.input_type, "text")
        self.assertIn("dd/mm/yyyy", form.fields["fecha"].widget.attrs.get("placeholder", ""))

    def test_export_excel_downloads_a_workbook(self):
        response = self.client.get(reverse("ahorros:exportar_excel"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_import_template_downloads_a_workbook(self):
        response = self.client.get(reverse("ahorros:plantilla_importacion"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
