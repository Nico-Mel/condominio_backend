from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Permiso, Rol, RolPermiso, Usuario


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
            'rol'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)
# accounts/serializers.py


class LoginSerializer(serializers.Serializer):
    ci = serializers.CharField()
    password = serializers.CharField(write_only=True)
