from django.db import models
from django.conf import settings
from django.utils import timezone

class Tarea(models.Model):
    TIPO_CHOICES = [
        ('ordinaria', 'Ordinaria'),
        ('extraordinaria', 'Extraordinaria'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    # Información básica
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='extraordinaria')
    
    # Asignación
    asignado_rol = models.ForeignKey('accounts.Rol', on_delete=models.CASCADE)
    # en models.py de Tarea
    creado_por = models.ForeignKey('accounts.Usuario', on_delete=models.CASCADE, related_name='tareas_creadas')

    # Estado y prioridad
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='media')
    
    # Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_limite = models.DateField(null=True, blank=True)
    
    # Cuando alguien la toma
    tomada_por = models.ForeignKey('accounts.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='tareas_tomadas')
    fecha_tomada = models.DateTimeField(null=True, blank=True)
    fecha_completada = models.DateTimeField(null=True, blank=True)
    
    # Ubicación opcional
    residencia = models.ForeignKey('condominio.Residencia', on_delete=models.SET_NULL, null=True, blank=True)
    area_comun = models.ForeignKey('condominio.AreaComun', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.titulo} - {self.get_estado_display()}"
    
    def tomar_tarea(self, usuario):
        """Método para que un usuario tome la tarea"""
        if self.tomada_por:
            raise ValueError("Esta tarea ya fue tomada por otro usuario")
        
        if usuario.rol != self.asignado_rol:
            raise ValueError("No tienes el rol requerido para esta tarea")
        
        self.tomada_por = usuario
        self.estado = 'en_progreso'
        self.fecha_tomada = timezone.now()
        self.save()
    
    def completar_tarea(self):
        """Método para marcar tarea como completada"""
        self.estado = 'completada'
        self.fecha_completada = timezone.now()
        self.save()

class Aviso(models.Model):
    TIPO_CHOICES = [
        ('general', 'General'),
        ('importante', 'Importante'), 
        ('urgente', 'Urgente'),
        ('mantenimiento', 'Mantenimiento'),
    ]
    
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='general')
    creado_por = models.ForeignKey('accounts.Usuario', on_delete=models.CASCADE)
    
    # Alcance
    para_todos = models.BooleanField(default=True)
    para_roles = models.ManyToManyField('accounts.Rol', blank=True)
    para_residencias = models.ManyToManyField('condominio.Residencia', blank=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    es_activo = models.BooleanField(default=True)
    
    # Push
    enviar_push = models.BooleanField(default=False)
    push_enviado = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.titulo} - {self.get_tipo_display()}"

class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('tarea', 'Tarea'),
        ('pago', 'Pago'),
        ('reserva', 'Reserva'),
        ('multa', 'Multa'),
        ('sistema', 'Sistema'),
        ('aviso', 'Aviso'),
    ]
    
    usuario = models.ForeignKey('accounts.Usuario', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    
    # Relación opcional
    entidad_tipo = models.CharField(max_length=50, blank=True)  # 'tarea', 'cuota', 'aviso'
    entidad_id = models.CharField(max_length=100, blank=True)   # ID de la entidad
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)
    fecha_leida = models.DateTimeField(null=True, blank=True)
    
    # Push (para implementación futura)
    push_enviado = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.usuario}: {self.titulo}"