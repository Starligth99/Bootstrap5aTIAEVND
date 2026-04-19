from django.contrib import admin

from .models import Deseo, Deuda, Gasto, GastoFijo, Ingreso, PagoDeuda


@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    list_display = ("fecha", "monto", "fuente", "nota")
    list_filter = ("fecha",)
    search_fields = ("fuente", "nota")


@admin.register(GastoFijo)
class GastoFijoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "monto", "dia_pago", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre", "nota")


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ("fecha", "monto", "categoria", "descripcion")
    list_filter = ("categoria", "fecha")
    search_fields = ("descripcion",)


class PagoDeudaInline(admin.TabularInline):
    model = PagoDeuda
    extra = 1


@admin.register(Deuda)
class DeudaAdmin(admin.ModelAdmin):
    list_display = ("acreedor", "monto_original", "fecha")
    search_fields = ("acreedor", "nota")
    inlines = [PagoDeudaInline]


@admin.register(PagoDeuda)
class PagoDeudaAdmin(admin.ModelAdmin):
    list_display = ("fecha", "monto", "deuda")
    list_filter = ("fecha",)


@admin.register(Deseo)
class DeseoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio", "prioridad", "comprado", "fecha_compra")
    list_filter = ("comprado", "prioridad")
    search_fields = ("nombre", "nota")
