# condominio/models.py
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from finance.models import Expensa, Cuota, DetalleCuota

class Unidad(models.Model):
    TIPO_UNIDAD_CHOICES = [
        ('casa', 'Casa'),
        ('departamento', 'Departamento'),
        ('local', 'Local Comercial'),
        ('oficina', 'Oficina'),
        ('otro', 'Otro'),
    ]
    
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('ocupada', 'Ocupada'),
        ('mantenimiento', 'En Mantenimiento'),
        ('reservada', 'Reservada'),
    ]
    
    id = models.AutoField(primary_key=True)
    tipo_unidad = models.CharField(max_length=20, choices=TIPO_UNIDAD_CHOICES)
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100, blank=True)
    
    # Campos para edificios (opcionales)
    edificio = models.CharField(max_length=100, blank=True, null=True)  
    piso = models.CharField(max_length=10, blank=True, null=True)       
    numero = models.CharField(max_length=10, blank=True, null=True)     
    
    dimensiones = models.CharField(max_length=100)
    habitaciones = models.PositiveIntegerField(default=1)
    banios = models.PositiveIntegerField(default=1)
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    precio_alquiler = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ubicacion = models.TextField()
    caracteristicas = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    esta_activa = models.BooleanField(default=True)
    foto_url = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = 'Unidad'
        verbose_name_plural = 'Unidades'

    def clean(self):
        """Validación contextual según tipo de unidad"""
        
        def campo_obligatorio(valor, nombre):
            if not valor or str(valor).strip() == "":
                raise ValidationError(f"El campo '{nombre}' es obligatorio para unidades tipo {self.tipo_unidad}")

        if self.tipo_unidad in ['departamento', 'local']:
            campo_obligatorio(self.edificio, "edificio")
            campo_obligatorio(self.numero, "número")

        elif self.tipo_unidad == 'casa':
            if self.edificio and self.edificio.strip() != "":
                raise ValidationError("Las casas no deben tener edificio asignado")
            if self.piso and self.piso.strip() != "":
                raise ValidationError("Las casas no deben tener piso asignado")
            
    def save(self, *args, **kwargs):
        self.clean()  # Ejecutar validaciones antes de guardar
        super().save(*args, **kwargs)

    def __str__(self):
        if self.edificio:
            return f"{self.edificio} - {self.codigo}"
        return f"{self.codigo} - {self.nombre or self.get_tipo_unidad_display()}"

class Residencia(models.Model):
    TIPO_CONTRATO_CHOICES = [
        ('propiedad', 'Propiedad'),
        ('alquiler', 'Alquiler'),
        ('comodato', 'Comodato'),
    ]
    
    id = models.AutoField(primary_key=True)
    residente = models.ForeignKey('accounts.Residente', on_delete=models.CASCADE, related_name='residencias')
    unidad = models.ForeignKey('Unidad', on_delete=models.CASCADE, related_name='residencias')
    
    tipo_contrato = models.CharField(max_length=20, choices=TIPO_CONTRATO_CHOICES)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)

    esta_activa = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    esta_activo = models.BooleanField(default=True)  # Soft delete

    class Meta:
        unique_together = [('unidad', 'esta_activa')]  # Una unidad solo una residencia activa
        verbose_name = 'Residencia'
        verbose_name_plural = 'Residencias'

    def clean(self):
        """Validación adicional para evitar múltiples residencias activas por unidad"""
        if self.esta_activa and self.esta_activo:
            residencias_activas = Residencia.objects.filter(
                unidad=self.unidad, 
                esta_activa=True,
                esta_activo=True
            ).exclude(pk=self.pk)
            
            if residencias_activas.exists():
                raise ValidationError(
                    f"Ya existe una residencia activa para la unidad {self.unidad.codigo}"
                )

    def save(self, *args, **kwargs):
            """Override save para generar cuota al crear residencia de alquiler"""
            # Primero validar y guardar
            self.clean()
            es_nuevo = self._state.adding  # True si es creación nueva
            
            super().save(*args, **kwargs)
            
            # Solo si es NUEVA residencia de alquiler ACTIVA
            if es_nuevo and self.tipo_contrato == 'alquiler' and self.esta_activa:
                self.generar_cuota_alquiler_actual()
    
    def generar_cuota_alquiler_actual(self):
        """Genera cuota de alquiler para el mes actual"""
        from django.utils import timezone
        from finance.models import Expensa, Cuota, DetalleCuota
        
        # 1. Verificar condiciones
        if not self.debe_generar_alquiler():
            return None
            
        # 2. Obtener periodo actual (YYYY-MM)
        periodo_actual = timezone.now().strftime('%Y-%m')
        
        # 3. Buscar o crear Expensa de Alquiler
        expensa_alquiler, creado = Expensa.objects.get_or_create(
            nombre="Alquiler Mensual",
            defaults={
                'tipo': 'alquiler', 
                'descripcion': 'Cuota mensual de alquiler de unidad',
                'es_activo': True
            }
        )
        
        # 4. Buscar o crear Cuota del periodo
        cuota, creada = Cuota.objects.get_or_create(
            residencia=self,
            periodo=periodo_actual,
            defaults={
                'fecha_emision': timezone.now().date(),
                'monto_total': 0  # Se recalcula con detalles
            }
        )
        
        # 5. Crear DetalleCuota para el alquiler
        detalle = DetalleCuota.objects.create(
            cuota=cuota,
            expensa=expensa_alquiler,
            monto=self.unidad.precio_alquiler,
            descripcion=f"Alquiler mensual - {periodo_actual}",
            referencia=f"ALQUILER_{self.id}_{periodo_actual}",
            fecha_vencimiento=self.calcular_fecha_vencimiento(periodo_actual)
        )
        
        return detalle
    
    def debe_generar_alquiler(self, periodo=None):
        """Verifica si debe generar cuota de alquiler"""
        from django.utils import timezone
        
        if periodo is None:
            periodo = timezone.now().strftime('%Y-%m')
            
        # Condiciones:
        # 1. Debe ser alquiler
        # 2. Debe estar activa
        # 3. Contrato debe estar vigente para el periodo
        # 4. No debe tener ya un detalle de alquiler para ese periodo
        
        if self.tipo_contrato != 'alquiler' or not self.esta_activa:
            return False
            
        # Verificar vigencia del contrato
        fecha_mes = timezone.datetime.strptime(periodo + '-01', '%Y-%m-%d').date()
        if self.fecha_inicio > fecha_mes:
            return False  # Contrato no ha empezado
        if self.fecha_fin and self.fecha_fin < fecha_mes:
            return False  # Contrato ya terminó
            
        # Verificar que no exista ya detalle de alquiler para este periodo
        from finance.models import DetalleCuota, Expensa
        existe_detalle = DetalleCuota.objects.filter(
            cuota__residencia=self,
            cuota__periodo=periodo,
            expensa__tipo='alquiler'
        ).exists()
        
        return not existe_detalle
    
    def calcular_fecha_vencimiento(self, periodo):
        """Calcula fecha de vencimiento (ej: día 5 del mes)"""
        from django.utils import timezone
        # Por ejemplo, día 5 de cada mes
        return timezone.datetime.strptime(periodo + '-05', '%Y-%m-%d').date()
    
    @property
    def cantidad_ocupantes(self):
        """Calcula la cantidad de ocupantes activos"""
        return self.habitantes.filter(esta_activo=True).count()

    def __str__(self):
        return f"{self.residente} → {self.unidad.codigo} ({self.tipo_contrato})"
    
    @property
    def duracion_contrato(self):
        if self.fecha_fin:
            return f"{self.fecha_inicio} a {self.fecha_fin}"
        return f"Indefinido desde {self.fecha_inicio}"

class Habitante(models.Model):
    TIPO_PARENTESCO_CHOICES = [
        ('conyuge', 'Cónyuge'),
        ('hijo', 'Hijo/Hija'),
        ('padre', 'Padre/Madre'),
        ('hermano', 'Hermano/Hermana'),
        ('otro_familiar', 'Otro Familiar'),
        ('amigo', 'Amigo/Conocido'),
    ]
    
    id = models.AutoField(primary_key=True)
    residente_titular = models.ForeignKey('accounts.Residente', on_delete=models.CASCADE, related_name='habitantes')
    residencia = models.ForeignKey('Residencia', on_delete=models.CASCADE, related_name='habitantes')
    
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    ci = models.CharField(max_length=20, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    tipo_parentesco = models.CharField(max_length=20, choices=TIPO_PARENTESCO_CHOICES)
    es_contacto_emergencia = models.BooleanField(default=False)
    
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    
    observaciones = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    esta_activo = models.BooleanField(default=True)  # Soft delete

    class Meta:
        verbose_name = 'Habitante'
        verbose_name_plural = 'Habitantes'

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.get_tipo_parentesco_display()})"
    
    @property
    def edad(self):
        if self.fecha_nacimiento:
            today = timezone.now().date()
            return today.year - self.fecha_nacimiento.year - (
                (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None
    
    @property
    def es_menor(self):
        return self.edad is not None and self.edad < 18

# Señal para actualizar contadores cuando cambien los habitantes
@receiver([post_save, post_delete], sender=Habitante)
def actualizar_contadores_residencia(sender, instance, **kwargs):
    """Actualizar contadores automáticamente cuando cambien los habitantes"""
    try:
        # Solo actualizar si el habitante está activo o se está eliminando
        if instance.esta_activo or kwargs.get('created') is False:
            instance.residencia.actualizar_contadores()
            instance.residencia.save()
    except Residencia.DoesNotExist:
        # Si la residencia fue eliminada, ignorar
        pass


# condominio/models.py (solo partes afectadas)

class AreaComun(models.Model):
    TIPO_AREA_CHOICES = [
        ('piscina', 'Piscina'),
        ('salon_eventos', 'Salón de Eventos'),
        ('gimnasio', 'Gimnasio'),
        ('parrilla', 'Quincho/Parilla'),
        ('cancha', 'Cancha Deportiva'),
        ('meeting', 'Meeting Room'),
        ('study', 'Study Room'),
        ('otro', 'Otro'),
    ]
    
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_AREA_CHOICES)
    descripcion = models.TextField(blank=True)
    capacidad = models.PositiveIntegerField(default=10)
    
    # Horarios básicos
    hora_apertura = models.TimeField(default='08:00')
    hora_cierre = models.TimeField(default='22:00')

    # Sistema de costos
    tiene_costo = models.BooleanField(default=False)
    costo_normal = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    costo_fin_semana = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    # Restricciones
    permitido_para_inquilinos = models.BooleanField(default=True)
    
    estado = models.CharField(max_length=20, choices=[
        ('disponible', 'Disponible'),
        ('mantenimiento', 'En Mantenimiento'),
    ], default='disponible')
    
    esta_activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Área Común'
        verbose_name_plural = 'Áreas Comunes'

    def __str__(self):
        return self.nombre
    
class ReservaAreaComun(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('reservada', 'Reservada'), 
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada')
    ]
    
    area_comun = models.ForeignKey('AreaComun', on_delete=models.CASCADE)
    residente = models.ForeignKey('accounts.Residente', on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    cuota_relacionada = models.ForeignKey('finance.Cuota', on_delete=models.SET_NULL, null=True, blank=True)
    detalle_cuota = models.ForeignKey('finance.DetalleCuota', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reserva de Área Común'
        verbose_name_plural = 'Reservas de Áreas Comunes'

    @property
    def costo(self):
        """Calcula el costo automáticamente"""
        if not self.area_comun.tiene_costo:
            return 0
        return self.area_comun.costo_fin_semana if self.fecha.weekday() in [5, 6] else self.area_comun.costo_normal

    def crear_cuota_reserva(self):
        """Crea la cuota y detalle de cuota - SUPER SIMPLE"""
        from finance.models import Expensa, Cuota, DetalleCuota
        
        if self.costo == 0:
            return None
            
        try:
            # 1. Expensa de reserva (CONCEPTO)
            expensa, _ = Expensa.objects.get_or_create(
                nombre="Reserva de Área Común",
                defaults={'tipo': 'reserva_area', 'es_activo': True}
            )
            
            # 2. Residencia activa del residente
            residencia = self.residente.residencias.filter(esta_activa=True).first()
            if not residencia:
                return None
                
            # 3. Cuota del mes (DOCUMENTO)
            periodo = self.fecha.strftime('%Y-%m')
            cuota, _ = Cuota.objects.get_or_create(
                residencia=residencia,
                periodo=periodo,
                defaults={'monto_total': 0, 'fecha_emision': timezone.now().date()}
            )
            
            # 4. DetalleCuota (LÍNEA de cobro)
            detalle = DetalleCuota.objects.create(
                cuota=cuota,
                expensa=expensa,
                monto=self.costo,
                descripcion=f"Reserva: {self.area_comun.nombre} - {self.fecha}",
                referencia=f"RESERVA_{self.id}",
                fecha_vencimiento=self.fecha
            )
            
            # 5. Guardar relaciones
            self.cuota_relacionada = cuota
            self.detalle_cuota = detalle
            self.save()
            
            return detalle
            
        except Exception as e:
            print(f"Error creando cuota: {e}")
            return None

    def cancelar_cuota_reserva(self):
        """ELIMINA el cobro si se cancela la reserva"""
        if self.detalle_cuota:
            self.detalle_cuota.delete()  # HARD DELETE
            self.detalle_cuota = None
            self.cuota_relacionada = None
            self.save()

    def save(self, *args, **kwargs):
        # Validación básica
        if self.hora_inicio >= self.hora_fin:
            from django.core.exceptions import ValidationError
            raise ValidationError("La hora de fin debe ser posterior al inicio")
        
        # Manejar cambios de estado
        if self.pk:
            original = ReservaAreaComun.objects.get(pk=self.pk)
            
            if original.estado == 'pendiente' and self.estado == 'reservada':
                super().save(*args, **kwargs)
                self.crear_cuota_reserva()  # Crear cobro
                return
                
            elif original.estado == 'reservada' and self.estado == 'cancelada':
                self.cancelar_cuota_reserva()  # Eliminar cobro
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reserva {self.area_comun.nombre} - {self.fecha}"