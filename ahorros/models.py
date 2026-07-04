from decimal import Decimal, ROUND_UP

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
    evidencia = models.ImageField(upload_to="evidencia/fijos/", blank=True, null=True)

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
    evidencia = models.ImageField(upload_to="evidencia/gastos/", blank=True, null=True)
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
    plazo_meses = models.PositiveSmallIntegerField(default=3, help_text="Cuántos meses planeas pagar esta deuda.")
    nota = models.CharField(max_length=255, blank=True)
    evidencia = models.ImageField(upload_to="evidencia/deudas/", blank=True, null=True)

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


class Deseo(models.Model):
    PRIORIDADES = [
        ("alta", "Alta"),
        ("media", "Media"),
        ("baja", "Baja"),
    ]

    nombre = models.CharField(max_length=120)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    prioridad = models.CharField(
        max_length=10, choices=PRIORIDADES, default="media"
    )
    nota = models.CharField(max_length=255, blank=True)
    imagen = models.ImageField(upload_to="evidencia/deseos/", blank=True, null=True)
    comprado = models.BooleanField(default=False)
    fecha_compra = models.DateField(null=True, blank=True)
    gasto = models.ForeignKey(
        Gasto,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="deseos",
        help_text="Gasto generado al marcar el deseo como comprado.",
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["comprado", "-creado_en"]
        verbose_name = "Deseo"
        verbose_name_plural = "Deseos"

    def __str__(self):
        return f"{self.nombre} · ${self.precio}"

    def falta(self, ahorro: Decimal) -> Decimal:
        """Monto que falta ahorrar para poder comprar este deseo."""
        pendiente = self.precio - ahorro
        return pendiente if pendiente > 0 else Decimal("0")

    def alcanza(self, ahorro: Decimal) -> bool:
        return ahorro >= self.precio

    def meses_para_ahorrar(self, ahorro_actual: Decimal, disponible_mensual: Decimal) -> int:
        if disponible_mensual <= Decimal("0"):
            return 0
        faltante = self.precio - ahorro_actual
        if faltante <= 0:
            return 0
        return int((faltante / disponible_mensual).quantize(Decimal("1."), rounding="ROUND_UP"))


class Nota(models.Model):
    titulo = models.CharField(max_length=120)
    contenido = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]
        verbose_name = "Nota"
        verbose_name_plural = "Notas"

    def __str__(self):
        return self.titulo


class Recordatorio(models.Model):
    titulo = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    fecha_recordatorio = models.DateField()
    completado = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["completado", "fecha_recordatorio", "-creado_en"]
        verbose_name = "Recordatorio"
        verbose_name_plural = "Recordatorios"

    def __str__(self):
        return f"{self.titulo} ({self.fecha_recordatorio})"


class HistoryEntry(models.Model):
    TIPO = [
        ("ingreso", "Ingreso"),
        ("gasto", "Gasto"),
        ("gasto_fijo", "Gasto fijo"),
        ("deuda", "Deuda"),
        ("pago_deuda", "Pago de deuda"),
        ("deseo", "Deseo"),
        ("nota", "Nota"),
        ("recordatorio", "Recordatorio"),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO)
    referencia = models.CharField(max_length=255, blank=True)
    monto = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    descripcion = models.CharField(max_length=255, blank=True)
    fecha = models.DateField(default=timezone.localdate)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-creado_en"]
        verbose_name = "Historial"
        verbose_name_plural = "Historial"

    def __str__(self):
        return f"{self.get_tipo_display()} · {self.referencia or self.descripcion}"
