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

    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, related_name='usuarios')

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.rol.nombre})"
