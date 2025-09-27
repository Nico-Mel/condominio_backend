# accounts/models.py
import uuid
from django.db import models


class Permiso(models.Model):
    """
    Permiso del sistema (crear usuario, ver reportes, etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Rol(models.Model):
    """
    Rol del sistema (administrador, guardia, copropietario, etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class RolPermiso(models.Model):
    """
    Relación Rol - Permiso (muchos a muchos controlado manualmente)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name='rol_permisos')
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE, related_name='rol_permisos')

    class Meta:
        unique_together = ('rol', 'permiso')
        verbose_name = "Rol-Permiso"
        verbose_name_plural = "Roles-Permisos"

    def __str__(self):
        return f"{self.rol.nombre} → {self.permiso.nombre}"



class Usuario(models.Model):
    """
    Usuario del sistema. Cada usuario pertenece a un Rol.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ci = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Cifrar manualmente si se requiere
    fecha_registro = models.DateTimeField(auto_now_add=True)
    esta_activo = models.BooleanField(default=True)
    foto_url = models.URLField(blank=True, null=True)

    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, related_name='usuarios')

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.rol.nombre})"
    # accounts/models.py (en tu modelo Usuario)

    @property
    def is_authenticated(self):
        return True


class Residente(models.Model):
    TIPO_RESIDENTE_CHOICES = [
        ('copropietario', 'Copropietario'),
        ('inquilino', 'Inquilino'),
        ('propietario', 'Propietario'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='residente')
    tipo = models.CharField(max_length=20, choices=TIPO_RESIDENTE_CHOICES)
    
    # Información de contacto adicional
    telefono = models.CharField(max_length=20, blank=True, null=True)
    
    # Contacto de emergencia PERSONAL
    contacto_emergencia_personal_nombre = models.CharField(max_length=100, blank=True, null=True)
    contacto_emergencia_personal_telefono = models.CharField(max_length=20, blank=True, null=True)
    contacto_emergencia_personal_parentesco = models.CharField(max_length=50, blank=True, null=True)
    
    # Vehículos y mascotas
    tiene_vehiculo = models.BooleanField(default=False)
    detalle_vehiculos = models.TextField(blank=True, null=True)
    tiene_mascota = models.BooleanField(default=False)
    detalle_mascotas = models.TextField(blank=True, null=True)
    
    # Fechas importantes
    fecha_ingreso = models.DateField(auto_now_add=False, null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.usuario.nombre} {self.usuario.apellido} ({self.tipo})"