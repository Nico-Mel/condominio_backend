# condominio/serializers.py
from rest_framework import serializers
from .models import Unidad, Residencia, Habitante, AreaComun, ReservaAreaComun

class UnidadSerializer(serializers.ModelSerializer):
    tipo_unidad_display = serializers.CharField(source='get_tipo_unidad_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    precio_venta_formateado = serializers.SerializerMethodField()
    precio_alquiler_formateado = serializers.SerializerMethodField()
    
    class Meta:
        model = Unidad
        fields = [
            'id', 'tipo_unidad', 'tipo_unidad_display', 'codigo', 'nombre', 'edificio', 'piso', 'numero',
            'dimensiones', 'habitaciones', 'banios', 'precio_venta', 'precio_venta_formateado',
            'precio_alquiler', 'precio_alquiler_formateado', 'ubicacion', 'caracteristicas',
            'estado', 'estado_display', 'fecha_creacion', 'esta_activa', 'foto_url'
        ]
    
    def get_precio_venta_formateado(self, obj):
        if obj.precio_venta:
            return f"${obj.precio_venta:,.2f}"
        return "No especificado"
    
    def get_precio_alquiler_formateado(self, obj):
        if obj.precio_alquiler:
            return f"${obj.precio_alquiler:,.2f}"
        return "No especificado"

class HabitanteSerializer(serializers.ModelSerializer):
    tipo_parentesco_display = serializers.CharField(source='get_tipo_parentesco_display', read_only=True)
    edad = serializers.ReadOnlyField()
    es_menor = serializers.ReadOnlyField()
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Habitante
        fields = [
            'id', 'residente_titular', 'residencia', 'nombre', 'apellido', 'nombre_completo',
            'ci', 'fecha_nacimiento', 'edad', 'es_menor', 'tipo_parentesco', 'tipo_parentesco_display',
            'es_contacto_emergencia', 'telefono', 'correo', 'observaciones', 'fecha_registro', 'esta_activo'
        ]
    
    def get_nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellido}"

class ResidenciaSerializer(serializers.ModelSerializer):
    tipo_contrato_display = serializers.CharField(source='get_tipo_contrato_display', read_only=True)
    duracion_contrato = serializers.ReadOnlyField()
    
    # Información relacionada para mostrar
    residente_nombre = serializers.CharField(source='residente.usuario.nombre', read_only=True)
    residente_apellido = serializers.CharField(source='residente.usuario.apellido', read_only=True)
    residente_ci = serializers.CharField(source='residente.usuario.ci', read_only=True)
    unidad_codigo = serializers.CharField(source='unidad.codigo', read_only=True)
    unidad_tipo = serializers.CharField(source='unidad.tipo_unidad', read_only=True)
    
    # Habitantes de esta residencia
    habitantes = HabitanteSerializer(many=True, read_only=True)
    
    class Meta:
        model = Residencia
        fields = [
            'id', 'residente', 'unidad', 'residente_nombre', 'residente_apellido', 'residente_ci',
            'unidad_codigo', 'unidad_tipo', 'tipo_contrato', 'tipo_contrato_display',
            'fecha_inicio', 'fecha_fin', 'duracion_contrato', 'esta_activa', 'fecha_registro', 
            'esta_activo', 'habitantes'
        ]
    
    def validate(self, data):
        unidad = data.get('unidad')
        residente = data.get('residente')
        
        # Validar que la unidad esté disponible (solo al crear)
        if self.instance is None and unidad and unidad.estado != 'disponible':
            raise serializers.ValidationError(
                f"La unidad {unidad.codigo} no está disponible. Estado actual: {unidad.estado}"
            )
        
        # Validar que el residente no tenga otra residencia activa (solo al crear)
        if self.instance is None and residente:
            residencias_activas = Residencia.objects.filter(
                residente=residente, 
                esta_activa=True
            )
            if residencias_activas.exists():
                raise serializers.ValidationError(
                    "El residente ya tiene una residencia activa"
                )
        
        # Validar fechas del contrato
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise serializers.ValidationError(
                "La fecha de inicio no puede ser posterior a la fecha de fin"
            )
            
        return data
    
    def create(self, validated_data):
        # Crear la residencia
        residencia = super().create(validated_data)
        
        # Actualizar el estado de la unidad a "ocupada"
        unidad = residencia.unidad
        unidad.estado = 'ocupada'
        unidad.save()
        
        return residencia
    
    def update(self, instance, validated_data):
        residencia = super().update(instance, validated_data)
        
        # Manejar cambios en el estado activo
        if 'esta_activa' in validated_data:
            unidad = residencia.unidad
            if validated_data['esta_activa']:
                unidad.estado = 'ocupada'
            else:
                unidad.estado = 'disponible'
            unidad.save()
            
        return residencia

# Serializer para crear habitantes dentro de una residencia
class HabitanteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habitante
        fields = [
            'id', 'residente_titular', 'residencia', 'nombre', 'apellido', 'ci',
            'fecha_nacimiento', 'tipo_parentesco', 'es_contacto_emergencia',
            'telefono', 'correo', 'observaciones'
        ]
    
    def validate(self, data):
        residencia = data.get('residencia')
        residente_titular = data.get('residente_titular')
        
        # Validar que el habitante pertenezca a la residencia correcta
        if residencia and residente_titular and residencia.residente != residente_titular:
            raise serializers.ValidationError(
                "El habitante debe pertenecer al residente titular de la residencia"
            )
            
        return data
    
# condominio/serializers.py 
class AreaComunSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    horario_funcionamiento = serializers.SerializerMethodField()
    
    class Meta:
        model = AreaComun
        fields = [
            'id', 'nombre', 'tipo', 'tipo_display', 'descripcion', 'capacidad',
            'hora_apertura', 'hora_cierre', 'horario_funcionamiento',
            'tiene_costo', 'costo_normal', 'costo_fin_semana',
            'permitido_para_inquilinos', 'estado', 'estado_display', 'esta_activa'
        ]
    
    def get_horario_funcionamiento(self, obj):
        return f"{obj.hora_apertura} - {obj.hora_cierre}"

# condominio/serializers.py (actualizar ReservaAreaComunSerializer)
class ReservaAreaComunSerializer(serializers.ModelSerializer):
    area_comun_nombre = serializers.CharField(source='area_comun.nombre', read_only=True)
    residente_nombre = serializers.SerializerMethodField()
    costo = serializers.ReadOnlyField()  # Usa la propiedad @property
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = ReservaAreaComun
        fields = '__all__'

    def get_residente_nombre(self, obj):
        return f"{obj.residente.usuario.nombre} {obj.residente.usuario.apellido}"

class ReservaAreaComunCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservaAreaComun
        fields = ['area_comun', 'fecha', 'hora_inicio', 'hora_fin']

    
    def validate(self, data):
        """Validaciones personalizadas para la creación"""
        from django.utils import timezone
        
        # Validar que la fecha no sea en el pasado
        if data['fecha'] < timezone.now().date():
            raise serializers.ValidationError("No se pueden hacer reservas para fechas pasadas")
        
        # Validar horario de funcionamiento del área común
        area_comun = data['area_comun']
        if data['hora_inicio'] < area_comun.hora_apertura:
            raise serializers.ValidationError(
                f"El área común abre a las {area_comun.hora_apertura}"
            )
        
        if data['hora_fin'] > area_comun.hora_cierre:
            raise serializers.ValidationError(
                f"El área común cierra a las {area_comun.hora_cierre}"
            )
        
        
        # Validar disponibilidad (no hay reservas superpuestas)
        reservas_existentes = ReservaAreaComun.objects.filter(
            area_comun=area_comun,
            fecha=data['fecha'],
            estado__in=['pendiente', 'reservada'],
            hora_inicio__lt=data['hora_fin'],
            hora_fin__gt=data['hora_inicio']
        )
        
        if reservas_existentes.exists():
            raise serializers.ValidationError(
                "El área común ya está reservada para ese horario"
            )
        
        return data

class ReservaAreaComunUpdateSerializer(serializers.ModelSerializer):
    """Serializer específico para actualizaciones (solo permite cambiar estado)"""
    class Meta:
        model = ReservaAreaComun
        fields = ['estado']
    
    def validate_estado(self, value):
        """Validar transiciones de estado permitidas"""
        instance = self.instance
        
        if instance.estado == 'cancelada' and value != 'cancelada':
            raise serializers.ValidationError("Una reserva cancelada no puede ser modificada")
        
        if instance.estado == 'completada' and value != 'completada':
            raise serializers.ValidationError("Una reserva completada no puede ser modificada")
        
        return value