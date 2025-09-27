from rest_framework import serializers
from .models import Expensa, Cuota, DetalleCuota, Pago
from django.db.models import Sum

class ExpensaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expensa
        fields = '__all__'

class DetalleCuotaSerializer(serializers.ModelSerializer):
    expensa_nombre = serializers.CharField(source='expensa.nombre', read_only=True)
    expensa_tipo = serializers.CharField(source='expensa.tipo', read_only=True)
    
    class Meta:
        model = DetalleCuota
        fields = [
            'id', 'expensa', 'expensa_nombre', 'expensa_tipo', 'monto', 
            'descripcion', 'referencia'
        ]

class CuotaSerializer(serializers.ModelSerializer):
    residencia_direccion = serializers.CharField(source='residencia.unidad.direccion', read_only=True)
    residente_nombre = serializers.CharField(source='residente.get_full_name', read_only=True)
    residente_uuid = serializers.UUIDField(source='residente.id', read_only=True)
    
    detalles = DetalleCuotaSerializer(many=True, read_only=True, source='detallecuota_set')
    monto_pendiente = serializers.SerializerMethodField()
    pagos_realizados = serializers.SerializerMethodField()
    
    class Meta:
        model = Cuota
        fields = [
            'id', 'residencia', 'residencia_direccion', 'residente_nombre', 'residente_uuid',
            'monto_total', 'monto_pendiente', 'pagos_realizados', 'estado', 
            'fecha_emision', 'periodo', 'detalles'
        ]
        read_only_fields = ['monto_total', 'fecha_emision']
    
    def get_monto_pendiente(self, obj):
        total_pagado = obj.pago_set.aggregate(total=Sum('monto_pagado'))['total'] or 0
        return max(0, obj.monto_total - total_pagado)
    
    def get_pagos_realizados(self, obj):
        return obj.pago_set.aggregate(total=Sum('monto_pagado'))['total'] or 0

class CuotaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuota
        fields = ['residencia', 'periodo']

class PagoCreateSerializer(serializers.ModelSerializer):
    """Serializer simplificado para creación de pagos"""
    class Meta:
        model = Pago
        fields = ['cuota', 'monto_pagado', 'metodo_pago']

class PagoSerializer(serializers.ModelSerializer):
    residente_nombre = serializers.CharField(source='residente.get_full_name', read_only=True)
    residente_uuid = serializers.UUIDField(source='residente.id', read_only=True)
    cuota_periodo = serializers.CharField(source='cuota.periodo', read_only=True)
    cuota_residencia = serializers.CharField(source='cuota.residencia.unidad.direccion', read_only=True)
    
    class Meta:
        model = Pago
        fields = [
            'id', 'cuota', 'cuota_periodo', 'cuota_residencia', 
            'residente', 'residente_nombre', 'residente_uuid',
            'monto_pagado', 'fecha_pago', 'metodo_pago'
        ]
        read_only_fields = ['fecha_pago']

# SERIALIZERS PARA RESIDENTES
class CuotaResidenteSerializer(serializers.ModelSerializer):
    residencia_direccion = serializers.CharField(source='residencia.unidad.direccion', read_only=True)
    detalles = DetalleCuotaSerializer(many=True, read_only=True, source='detallecuota_set')
    monto_pendiente = serializers.SerializerMethodField()
    pagos_realizados = serializers.SerializerMethodField()
    
    class Meta:
        model = Cuota
        fields = [
            'id', 'residencia_direccion', 'monto_total', 'monto_pendiente',
            'pagos_realizados', 'estado', 'fecha_emision', 'periodo', 'detalles'
        ]
    
    def get_monto_pendiente(self, obj):
        total_pagado = obj.pago_set.aggregate(total=Sum('monto_pagado'))['total'] or 0
        return max(0, obj.monto_total - total_pagado)
    
    def get_pagos_realizados(self, obj):
        return obj.pago_set.aggregate(total=Sum('monto_pagado'))['total'] or 0

class PagoResidenteSerializer(serializers.ModelSerializer):
    cuota_periodo = serializers.CharField(source='cuota.periodo', read_only=True)
    cuota_residencia = serializers.CharField(source='cuota.residencia.unidad.direccion', read_only=True)
    
    class Meta:
        model = Pago
        fields = [
            'id', 'cuota_periodo', 'cuota_residencia', 'monto_pagado', 
            'fecha_pago', 'metodo_pago'
        ]

class DetalleCuotaCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para creación de detalles"""
    class Meta:
        model = DetalleCuota
        fields = ['cuota', 'expensa', 'monto', 'descripcion', 'referencia']

class ExpensaCreateSerializer(serializers.ModelSerializer):
    """Serializer simplificado para creación de expensas"""
    class Meta:
        model = Expensa
        fields = ['nombre', 'tipo', 'descripcion']