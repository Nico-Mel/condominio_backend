from rest_framework import serializers
from .models import Tarea, Aviso, Notificacion
from accounts.serializers import UsuarioSerializer 

class TareaSerializer(serializers.ModelSerializer):
    creado_por_nombre = serializers.CharField(source='creado_por.get_full_name', read_only=True)
    tomada_por_nombre = serializers.CharField(source='tomada_por.get_full_name', read_only=True)
    asignado_rol_nombre = serializers.CharField(source='asignado_rol.nombre', read_only=True)
    residencia_direccion = serializers.CharField(source='residencia.direccion', read_only=True, allow_null=True)
    area_comun_nombre = serializers.CharField(source='area_comun.nombre', read_only=True, allow_null=True)
    
    class Meta:
        model = Tarea
        fields = '__all__'
        read_only_fields = ['fecha_creacion', 'tomada_por', 'fecha_tomada', 'fecha_completada', 'creado_por']

class TareaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarea
        fields = ['titulo', 'descripcion', 'tipo', 'asignado_rol', 'prioridad', 'fecha_limite', 'residencia', 'area_comun']

class TomarTareaSerializer(serializers.Serializer):
    # Serializer simple para la acción de tomar tarea
    confirmacion = serializers.BooleanField(default=True)

class CompletarTareaSerializer(serializers.Serializer):
    observaciones = serializers.CharField(required=False, allow_blank=True)

# Añadir después de los serializers de Tarea

class AvisoSerializer(serializers.ModelSerializer):
    creado_por_nombre = serializers.CharField(source='creado_por.get_full_name', read_only=True)
    para_roles_nombres = serializers.SerializerMethodField()
    para_residencias_direcciones = serializers.SerializerMethodField()
    
    class Meta:
        model = Aviso
        fields = '__all__'
        read_only_fields = ['fecha_creacion', 'push_enviado', 'creado_por']
    
    def get_para_roles_nombres(self, obj):
        return [rol.nombre for rol in obj.para_roles.all()]
    
    def get_para_residencias_direcciones(self, obj):
        return [residencia.direccion for residencia in obj.para_residencias.all()]

class AvisoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aviso
        fields = ['titulo', 'contenido', 'tipo', 'para_todos', 'para_roles', 'para_residencias', 'fecha_expiracion', 'enviar_push']

class NotificacionSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    
    class Meta:
        model = Notificacion
        fields = '__all__'
        read_only_fields = ['fecha_creacion', 'push_enviado']

class MarcarLeidaSerializer(serializers.Serializer):
    leida = serializers.BooleanField(default=True)