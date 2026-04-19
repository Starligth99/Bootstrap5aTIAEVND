import calendar
import json
from datetime import date, timedelta
from decimal import Decimal

from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    DeudaForm,
    GastoFijoForm,
    GastoForm,
    IngresoForm,
    PagoDeudaForm,
)
from .models import Deuda, Gasto, GastoFijo, Ingreso, PagoDeuda


def _rango_semana(hoy: date) -> tuple[date, date]:
    """Lunes y domingo de la semana que contiene `hoy`."""
    lunes = hoy - timedelta(days=hoy.weekday())
    domingo = lunes + timedelta(days=6)
    return lunes, domingo


def _rango_mes(hoy: date) -> tuple[date, date]:
    inicio = hoy.replace(day=1)
    ultimo = hoy.replace(day=calendar.monthrange(hoy.year, hoy.month)[1])
    return inicio, ultimo


def _sumar(qs, campo: str = "monto") -> Decimal:
    return qs.aggregate(total=Sum(campo))["total"] or Decimal("0")


def dashboard(request):
    hoy = timezone.localdate()
    lunes, domingo = _rango_semana(hoy)
    inicio_mes, fin_mes = _rango_mes(hoy)

    # Métricas de la semana
    ingresos_semana = _sumar(
        Ingreso.objects.filter(fecha__range=(lunes, domingo))
    )
    gastos_semana = _sumar(
        Gasto.objects.filter(fecha__range=(lunes, domingo))
    )

    # Métricas del mes
    ingresos_mes = _sumar(
        Ingreso.objects.filter(fecha__range=(inicio_mes, fin_mes))
    )
    gastos_mes = _sumar(
        Gasto.objects.filter(fecha__range=(inicio_mes, fin_mes))
    )

    # Gastos fijos del mes
    fijos_activos = GastoFijo.objects.filter(activo=True)
    fijos_total_mes = _sumar(fijos_activos)
    fijos_pendientes_qs = fijos_activos.filter(dia_pago__gte=hoy.day)
    fijos_pendientes_total = _sumar(fijos_pendientes_qs)

    # Disponible para ahorrar en el mes:
    # lo que entra - lo que ya gasté - lo que debo cubrir de fijos aún
    disponible_ahorro = (
        ingresos_mes - gastos_mes - fijos_pendientes_total
    )

    # Disponible en la semana (sin contar fijos, sólo flujo semanal)
    disponible_semana = ingresos_semana - gastos_semana

    # Deudas
    deudas = list(Deuda.objects.all())
    total_deuda_original = sum(
        (d.monto_original for d in deudas), Decimal("0")
    )
    total_deuda_saldo = sum((d.saldo() for d in deudas), Decimal("0"))
    total_deuda_pagado = total_deuda_original - total_deuda_saldo

    # Chart: ingresos vs gastos por semana del mes actual
    semanas_labels = []
    semanas_ingresos = []
    semanas_gastos = []
    cursor = inicio_mes
    idx = 1
    while cursor <= fin_mes:
        semana_lunes = cursor - timedelta(days=cursor.weekday())
        semana_domingo = semana_lunes + timedelta(days=6)
        rango_inicio = max(semana_lunes, inicio_mes)
        rango_fin = min(semana_domingo, fin_mes)
        semanas_labels.append(f"Sem {idx}")
        semanas_ingresos.append(
            float(
                _sumar(Ingreso.objects.filter(fecha__range=(rango_inicio, rango_fin)))
            )
        )
        semanas_gastos.append(
            float(
                _sumar(Gasto.objects.filter(fecha__range=(rango_inicio, rango_fin)))
            )
        )
        cursor = semana_domingo + timedelta(days=1)
        idx += 1

    contexto = {
        "hoy": hoy,
        "lunes": lunes,
        "domingo": domingo,
        "inicio_mes": inicio_mes,
        "fin_mes": fin_mes,
        "ingresos_semana": ingresos_semana,
        "gastos_semana": gastos_semana,
        "disponible_semana": disponible_semana,
        "ingresos_mes": ingresos_mes,
        "gastos_mes": gastos_mes,
        "fijos_total_mes": fijos_total_mes,
        "fijos_pendientes_total": fijos_pendientes_total,
        "fijos_pendientes": fijos_pendientes_qs,
        "disponible_ahorro": disponible_ahorro,
        "deudas": deudas,
        "total_deuda_original": total_deuda_original,
        "total_deuda_saldo": total_deuda_saldo,
        "total_deuda_pagado": total_deuda_pagado,
        "ultimos_ingresos": Ingreso.objects.all()[:5],
        "ultimos_gastos": Gasto.objects.all()[:5],
        "chart_labels": json.dumps(semanas_labels),
        "chart_ingresos": json.dumps(semanas_ingresos),
        "chart_gastos": json.dumps(semanas_gastos),
    }
    return render(request, "ahorros/dashboard.html", contexto)


# ---------- Ingresos ----------
def ingresos_lista(request):
    if request.method == "POST":
        form = IngresoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ingreso registrado.")
            return redirect("ahorros:ingresos")
    else:
        form = IngresoForm()
    return render(
        request,
        "ahorros/ingresos.html",
        {"form": form, "objetos": Ingreso.objects.all()},
    )


@require_POST
def ingreso_borrar(request, pk):
    obj = get_object_or_404(Ingreso, pk=pk)
    obj.delete()
    messages.info(request, "Ingreso eliminado.")
    return redirect("ahorros:ingresos")


# ---------- Gastos ----------
def gastos_lista(request):
    if request.method == "POST":
        form = GastoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Gasto registrado.")
            return redirect("ahorros:gastos")
    else:
        form = GastoForm()
    return render(
        request,
        "ahorros/gastos.html",
        {"form": form, "objetos": Gasto.objects.all()},
    )


@require_POST
def gasto_borrar(request, pk):
    obj = get_object_or_404(Gasto, pk=pk)
    obj.delete()
    messages.info(request, "Gasto eliminado.")
    return redirect("ahorros:gastos")


# ---------- Gastos fijos ----------
def fijos_lista(request):
    if request.method == "POST":
        form = GastoFijoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Gasto fijo guardado.")
            return redirect("ahorros:fijos")
    else:
        form = GastoFijoForm()
    return render(
        request,
        "ahorros/fijos.html",
        {"form": form, "objetos": GastoFijo.objects.all()},
    )


@require_POST
def fijo_borrar(request, pk):
    obj = get_object_or_404(GastoFijo, pk=pk)
    obj.delete()
    messages.info(request, "Gasto fijo eliminado.")
    return redirect("ahorros:fijos")


# ---------- Deudas ----------
def deudas_lista(request):
    if request.method == "POST":
        form = DeudaForm(request.POST)
        if form.is_valid():
            deuda = form.save()
            messages.success(request, "Deuda registrada.")
            return redirect("ahorros:deuda_detalle", pk=deuda.pk)
    else:
        form = DeudaForm()
    return render(
        request,
        "ahorros/deudas.html",
        {"form": form, "objetos": Deuda.objects.all()},
    )


def deuda_detalle(request, pk):
    deuda = get_object_or_404(Deuda, pk=pk)
    if request.method == "POST":
        form = PagoDeudaForm(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.deuda = deuda
            pago.save()
            messages.success(
                request,
                f"Pago de ${pago.monto} registrado. Saldo actual: ${deuda.saldo()}.",
            )
            return redirect("ahorros:deuda_detalle", pk=deuda.pk)
    else:
        form = PagoDeudaForm()
    return render(
        request,
        "ahorros/deuda_detalle.html",
        {"deuda": deuda, "pagos": deuda.pagos.all(), "form": form},
    )


@require_POST
def deuda_borrar(request, pk):
    obj = get_object_or_404(Deuda, pk=pk)
    obj.delete()
    messages.info(request, "Deuda eliminada.")
    return redirect("ahorros:deudas")


@require_POST
def pago_borrar(request, pk, pago_pk):
    pago = get_object_or_404(PagoDeuda, pk=pago_pk, deuda_id=pk)
    pago.delete()
    messages.info(request, "Pago eliminado.")
    return HttpResponseRedirect(reverse("ahorros:deuda_detalle", args=[pk]))
