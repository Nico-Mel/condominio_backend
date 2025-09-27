#finance/models.py
from django.db import models
from django.db.models import Sum

class Expensa(models.Model):
    TIPO_EXPENSA_CHOICES = [
        ('alquiler', 'Alquiler'),
        ('reserva_area', 'Reserva de Área Común'),
        ('expensa_ordinaria', 'Expensa Ordinaria'),
        ('multa', 'Multa'),
        ('servicio', 'Servicio'),
    ]
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_EXPENSA_CHOICES)
    descripcion = models.TextField(blank=True)
    es_activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Cuota(models.Model):
    residencia = models.ForeignKey('condominio.Residencia', on_delete=models.CASCADE)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'), 
        ('pagado', 'Pagado'),
        ('parcial', 'Parcial')
    ], default='pendiente')
    fecha_emision = models.DateField(auto_now_add=True)
    periodo = models.CharField(max_length=7)  # Formato: YYYY-MM

    class Meta:
        unique_together = ['residencia', 'periodo']

    @property
    def detalles_expensas(self):
        return self.detallecuota_set.all()

    def calcular_monto_total(self):
        """Recalcula el monto total basado en los detalles"""
        total = self.detallecuota_set.aggregate(
            total=Sum('monto')
        )['total'] or 0
        self.monto_total = total
        self.save()
        return total

    @property
    def residente(self):
        return self.residencia.residente

    def __str__(self):
        return f"Cuota {self.residencia} - {self.periodo} - ${self.monto_total}"

# finance/models.py - DetalleCuota SIMPLIFICADO
class DetalleCuota(models.Model):
    cuota = models.ForeignKey('Cuota', on_delete=models.CASCADE)
    expensa = models.ForeignKey('Expensa', on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True)
    referencia = models.CharField(max_length=100, blank=True)
    
    # SOLO fecha_vencimiento, NADA de esta_activo
    fecha_vencimiento = models.DateField(null=True, blank=True)
   
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.cuota.calcular_monto_total()

    def __str__(self):
        return f"Detalle: {self.expensa.nombre} - ${self.monto}"

class Pago(models.Model):
    cuota = models.ForeignKey('Cuota', on_delete=models.CASCADE)
    residente = models.ForeignKey('accounts.Residente', on_delete=models.CASCADE)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=100, choices=[
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('tarjeta', 'Tarjeta'),
    ])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Recalcular estado de la cuota
        total_pagado = self.cuota.pago_set.aggregate(
            total=Sum('monto_pagado')
        )['total'] or 0
        
        if total_pagado >= self.cuota.monto_total:
            self.cuota.estado = 'pagado'
        elif total_pagado > 0:
            self.cuota.estado = 'parcial'
        else:
            self.cuota.estado = 'pendiente'
            
        self.cuota.save()

    def __str__(self):
        return f"Pago {self.residente} - ${self.monto_pagado}"