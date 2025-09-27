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
    
class Multa(models.Model):
    residencia = models.ForeignKey('condominio.Residencia', on_delete=models.CASCADE, null=True, blank=True)
    residente = models.ForeignKey('accounts.Residente', on_delete=models.CASCADE, null=True, blank=True)

    monto = models.DecimalField(max_digits=10, decimal_places=2)
    motivo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_incidente = models.DateField()
    fecha_creacion = models.DateField(auto_now_add=True)
    
    creado_por = models.ForeignKey('accounts.Usuario', on_delete=models.CASCADE)
    detalle_cuota = models.OneToOneField('DetalleCuota', on_delete=models.SET_NULL, null=True, blank=True)

    def convertir_a_detalle_cuota(self, periodo=None):
        """Convierte la multa en un DetalleCuota para el periodo actual"""
        from django.utils import timezone
        
        if self.detalle_cuota:
            return self.detalle_cuota
            
        if periodo is None:
            periodo = timezone.now().strftime('%Y-%m')
        
        # Determinar residencia (prioridad: residencia directa > residente.residencia)
        residencia_target = self.residencia
        if not residencia_target and self.residente:
            residencia_target = self.residente.residencia
            
        if not residencia_target:
            raise ValueError("Multa debe tener residencia o residente asociado")
        
        expensa_multa, _ = Expensa.objects.get_or_create(
            nombre="Multa por Infracción",
            defaults={
                'tipo': 'multa',
                'descripcion': 'Multa por incumplimiento de normas del condominio',
                'es_activo': True
            }
        )

        cuota, _ = Cuota.objects.get_or_create(
            residencia=residencia_target,
            periodo=periodo,
            defaults={'fecha_emision': timezone.now().date()}
        )
        
        detalle = DetalleCuota.objects.create(
            cuota=cuota,
            expensa=expensa_multa,
            monto=self.monto,
            descripcion=f"Multa: {self.motivo} - {self.descripcion}",
            referencia=f"MULTA_{self.id}",
            fecha_vencimiento=timezone.now().date().replace(day=10)  # Vence el 10 del mes
        )
        
        self.detalle_cuota = detalle
        self.save()
        
        return detalle

    @property
    def estado(self):
        """Estado basado en el detalle_cuota asociado"""
        if not self.detalle_cuota:
            return 'pendiente'
        return self.detalle_cuota.cuota.estado

    def save(self, *args, **kwargs):
        """Al guardar, si es nueva y tiene datos suficientes, convertir automáticamente"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Si es nueva y tiene residencia/residente, convertir automáticamente
        if is_new and (self.residencia or self.residente):
            try:
                self.convertir_a_detalle_cuota()
            except Exception as e:
                # Log error pero no fallar el guardado
                print(f"Error convirtiendo multa a detalle: {e}")

    def __str__(self):
        residente_nombre = self.residente.user.get_full_name() if self.residente else "Sin residente"
        return f"Multa {residente_nombre} - ${self.monto} - {self.estado}"