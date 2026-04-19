from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Ingreso(models.Model):
    fecha = models.DateField(default=timezone.localdate)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fuente = models.CharField(
        max_length=100,
        blank=True,
        help_text="De dónde viene (sueldo, freelance, venta, etc.)",
    )
    nota = models.CharField(max_length=255, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-creado_en"]
        verbose_name = "Ingreso"
        verbose_name_plural = "Ingresos"

    def __str__(self):
        return f"{self.fecha} · ${self.monto}"


class GastoFijo(models.Model):
    nombre = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    dia_pago = models.PositiveSmallIntegerField(
        default=1,
        help_text="Día del mes en que vence el pago (1-31).",
    )
    activo = models.BooleanField(default=True)
    nota = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["dia_pago", "nombre"]
        verbose_name = "Gasto fijo"
        verbose_name_plural = "Gastos fijos"

    def __str__(self):
        return f"{self.nombre} (${self.monto})"


class Gasto(models.Model):
    CATEGORIAS = [
        ("comida", "Comida"),
        ("transporte", "Transporte"),
        ("diversion", "Diversión"),
        ("personal", "Personal"),
        ("hogar", "Hogar"),
        ("otro", "Otro"),
    ]

    fecha = models.DateField(default=timezone.localdate)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default="otro")
    descripcion = models.CharField(max_length=255, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-creado_en"]
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"

    def __str__(self):
        return f"{self.fecha} · {self.get_categoria_display()} · ${self.monto}"


class Deuda(models.Model):
    acreedor = models.CharField(max_length=100, help_text="A quién le debes.")
    monto_original = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField(default=timezone.localdate)
    nota = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-fecha", "acreedor"]
        verbose_name = "Deuda"
        verbose_name_plural = "Deudas"

    def total_pagado(self) -> Decimal:
        return self.pagos.aggregate(total=Sum("monto"))["total"] or Decimal("0")

    def saldo(self) -> Decimal:
        return self.monto_original - self.total_pagado()

    def liquidada(self) -> bool:
        return self.saldo() <= Decimal("0")

    def __str__(self):
        return f"{self.acreedor} · ${self.monto_original}"


class PagoDeuda(models.Model):
    deuda = models.ForeignKey(
        Deuda, related_name="pagos", on_delete=models.CASCADE
    )
    fecha = models.DateField(default=timezone.localdate)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    nota = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-fecha", "-id"]
        verbose_name = "Pago de deuda"
        verbose_name_plural = "Pagos de deudas"

    def __str__(self):
        return f"{self.fecha} · ${self.monto} → {self.deuda.acreedor}"
