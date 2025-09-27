# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Permiso, Rol, RolPermiso, Usuario, Residente


class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = ['id', 'nombre']


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion']


class RolPermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolPermiso
        fields = ['id', 'rol', 'permiso']


class UsuarioSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id',
            'ci',
            'nombre',
            'apellido',
            'correo',
            'password',
            'fecha_registro',
            'esta_activo',
            'rol',
            'rol_nombre',
            'foto_url',
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_rol_nombre(self, obj):
        return obj.rol.nombre if obj.rol else None
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)


class LoginSerializer(serializers.Serializer):
    ci = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ResidenteSerializer(serializers.ModelSerializer):
    usuario_info = UsuarioSerializer(source='usuario', read_only=True)
    nombre_completo = serializers.SerializerMethodField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Residente
        fields = [
            'id', 'usuario', 'usuario_info', 'nombre_completo', 'tipo', 'tipo_display',
            'telefono', 'contacto_emergencia_personal_nombre', 
            'contacto_emergencia_personal_telefono', 'contacto_emergencia_personal_parentesco',
            'tiene_vehiculo', 'detalle_vehiculos', 'tiene_mascota', 'detalle_mascotas',
            'fecha_ingreso', 'observaciones'
        ]
    
    def get_nombre_completo(self, obj):
        return f"{obj.usuario.nombre} {obj.usuario.apellido}"
    
    def create(self, validated_data):
        # CORREGIR: los nombres de roles deben coincidir exactamente
        usuario = validated_data['usuario']
        if usuario.rol.nombre != 'Residente':
            raise serializers.ValidationError("El usuario debe tener rol 'Residente' para registrar como residente.")
        return super().create(validated_data)