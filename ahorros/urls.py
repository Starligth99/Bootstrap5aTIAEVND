from django.urls import path

from . import views

app_name = "ahorros"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    # Ingresos
    path("ingresos/", views.ingresos_lista, name="ingresos"),
    path(
        "ingresos/<int:pk>/borrar/",
        views.ingreso_borrar,
        name="ingreso_borrar",
    ),
    # Gastos
    path("gastos/", views.gastos_lista, name="gastos"),
    path("gastos/<int:pk>/borrar/", views.gasto_borrar, name="gasto_borrar"),
    # Gastos fijos
    path("fijos/", views.fijos_lista, name="fijos"),
    path("fijos/<int:pk>/borrar/", views.fijo_borrar, name="fijo_borrar"),
    # Deudas
    path("deudas/", views.deudas_lista, name="deudas"),
    path("deudas/<int:pk>/", views.deuda_detalle, name="deuda_detalle"),
    path("deudas/<int:pk>/borrar/", views.deuda_borrar, name="deuda_borrar"),
    path(
        "deudas/<int:pk>/pagos/<int:pago_pk>/borrar/",
        views.pago_borrar,
        name="pago_borrar",
    ),
]
