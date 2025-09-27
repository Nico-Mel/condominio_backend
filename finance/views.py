from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Cuota, Pago, Expensa, DetalleCuota, Multa
from .serializers import (
    CuotaSerializer, CuotaCreateSerializer, CuotaResidenteSerializer,
    PagoSerializer, PagoCreateSerializer, PagoResidenteSerializer,
    ExpensaSerializer, DetalleCuotaSerializer, DetalleCuotaCreateSerializer,
    MultaSerializer
)

# VIEWS PARA EXPENSAS (Administrador)
class ExpensaListCreateAPIView(APIView):
    """Vista para listar y crear expensas (solo admin)"""
    def get(self, request):
        expensas = Expensa.objects.all()
        serializer = ExpensaSerializer(expensas, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ExpensaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExpensaDetailAPIView(APIView):
    """Vista para detalle, actualizar y eliminar expensas"""
    def get(self, request, pk):
        expensa = get_object_or_404(Expensa, pk=pk)
        serializer = ExpensaSerializer(expensa)
        return Response(serializer.data)

    def patch(self, request, pk):
        expensa = get_object_or_404(Expensa, pk=pk)
        serializer = ExpensaSerializer(expensa, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        expensa = get_object_or_404(Expensa, pk=pk)
        # En lugar de eliminar, desactivamos
        expensa.es_activo = False
        expensa.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

# VIEWS PARA DETALLES DE CUOTA (Administrador)
class DetalleCuotaListCreateAPIView(APIView):
    """Vista para listar y crear detalles de cuota"""
    def get(self, request):
        detalles = DetalleCuota.objects.all()
        serializer = DetalleCuotaSerializer(detalles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DetalleCuotaCreateSerializer(data=request.data)
        if serializer.is_valid():
            detalle = serializer.save()
            # Recalcular el total de la cuota automáticamente
            detalle.cuota.calcular_monto_total()
            detalle_serializer = DetalleCuotaSerializer(detalle)
            return Response(detalle_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DetalleCuotaDetailAPIView(APIView):
    """Vista para detalle, actualizar y eliminar detalles de cuota"""
    def get(self, request, pk):
        detalle = get_object_or_404(DetalleCuota, pk=pk)
        serializer = DetalleCuotaSerializer(detalle)
        return Response(serializer.data)

    def patch(self, request, pk):
        detalle = get_object_or_404(DetalleCuota, pk=pk)
        serializer = DetalleCuotaSerializer(detalle, data=request.data, partial=True)
        if serializer.is_valid():
            detalle_actualizado = serializer.save()
            # Recalcular el total de la cuota
            detalle_actualizado.cuota.calcular_monto_total()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        detalle = get_object_or_404(DetalleCuota, pk=pk)
        cuota = detalle.cuota  # Guardar referencia antes de eliminar
        detalle.delete()
        # Recalcular el total de la cuota después de eliminar
        cuota.calcular_monto_total()
        return Response(status=status.HTTP_204_NO_CONTENT)

# VIEWS PARA CUOTAS (Administrador) 
class CuotaListCreateAPIView(APIView):
    def get(self, request):
        cuotas = Cuota.objects.all()
        serializer = CuotaSerializer(cuotas, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CuotaCreateSerializer(data=request.data)
        if serializer.is_valid():
            cuota = serializer.save()
            # Podemos agregar detalles por defecto si es necesario
            cuota_serializer = CuotaSerializer(cuota)
            return Response(cuota_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CuotaDetailAPIView(APIView):
    def get(self, request, pk):
        cuota = get_object_or_404(Cuota, pk=pk)
        serializer = CuotaSerializer(cuota)
        return Response(serializer.data)

    def patch(self, request, pk):
        cuota = get_object_or_404(Cuota, pk=pk)
        serializer = CuotaSerializer(cuota, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# VIEWS PARA PAGOS (Administrador) 
class PagoListCreateAPIView(APIView):
    def get(self, request):
        pagos = Pago.objects.all()
        serializer = PagoSerializer(pagos, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PagoCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Si no se especifica residente, usar el autenticado
            residente = request.data.get('residente') or request.user.residente
            pago = serializer.save(residente=residente)
            pago_serializer = PagoSerializer(pago)
            return Response(pago_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PagoDetailAPIView(APIView):
    def get(self, request, pk):
        pago = get_object_or_404(Pago, pk=pk)
        serializer = PagoSerializer(pago)
        return Response(serializer.data)

    def delete(self, request, pk):
        pago = get_object_or_404(Pago, pk=pk)
        cuota = pago.cuota  # Guardar referencia antes de eliminar
        pago.delete()
        # Recalcular estado de la cuota después de eliminar pago
        cuota.calcular_monto_total()
        return Response(status=status.HTTP_204_NO_CONTENT)

# VIEWS ESPECIALES PARA RESIDENTES
class MisCuotasAPIView(APIView):
    """Vista para que un residente vea SUS cuotas"""
    def get(self, request):
        residente = request.user.residente
        cuotas = Cuota.objects.filter(residencia__residente=residente)
        serializer = CuotaResidenteSerializer(cuotas, many=True)
        return Response(serializer.data)

class MisPagosAPIView(APIView):
    """Vista para que un residente vea SUS pagos"""
    def get(self, request):
        residente = request.user.residente
        pagos = Pago.objects.filter(residente=residente)
        serializer = PagoResidenteSerializer(pagos, many=True)
        return Response(serializer.data)

class RealizarPagoAPIView(APIView):
    """Vista para que un residente realice un pago"""
    def post(self, request):
        serializer = PagoCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Validar que la cuota pertenece al residente
            cuota = serializer.validated_data['cuota']
            if cuota.residencia.residente != request.user.residente:
                return Response(
                    {"error": "No puedes pagar una cuota que no es tuya"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            pago = serializer.save(residente=request.user.residente)
            pago_serializer = PagoResidenteSerializer(pago)
            return Response(pago_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# VISTAS ADICIONALES ÚTILES
class CuotasPorResidenteAPIView(APIView):
    """Vista para administrador: ver cuotas de un residente específico"""
    def get(self, request, residente_id):
        cuotas = Cuota.objects.filter(residencia__residente_id=residente_id)
        serializer = CuotaSerializer(cuotas, many=True)
        return Response(serializer.data)

class CuotasPorPeriodoAPIView(APIView):
    """Vista para administrador: ver cuotas de un período específico"""
    def get(self, request, periodo):
        cuotas = Cuota.objects.filter(periodo=periodo)
        serializer = CuotaSerializer(cuotas, many=True)
        return Response(serializer.data)

class GenerarCuotasMensualesAPIView(APIView):
    """Vista para administrador: generar cuotas automáticamente para todos"""
    def post(self, request):
        from condominio.models import Residencia
        periodo = request.data.get('periodo')  # Formato: YYYY-MM
        
        # Lógica para generar cuotas automáticamente
        # (esto sería más complejo en la realidad)
        residencias = Residencia.objects.filter(esta_activa=True)
        cuotas_creadas = []
        
        for residencia in residencias:
            cuota, created = Cuota.objects.get_or_create(
                residencia=residencia,
                periodo=periodo,
                defaults={'monto_total': 0}
            )
            if created:
                cuotas_creadas.append(cuota)
        
        serializer = CuotaSerializer(cuotas_creadas, many=True)
        return Response({
            "message": f"Se generaron {len(cuotas_creadas)} cuotas para el período {periodo}",
            "cuotas": serializer.data
        }, status=status.HTTP_201_CREATED)
    
# VIEWS PARA MULTAS (Administrador)
class MultaListCreateAPIView(APIView):
    """Vista para listar y crear multas"""
    
    def get(self, request):
        multas = Multa.objects.all().order_by('-fecha_creacion')
        serializer = MultaSerializer(multas, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MultaSerializer(data=request.data)
        if serializer.is_valid():
            # Asignar automáticamente el usuario creador
            multa = serializer.save(creado_por=request.user)
            
            # La conversión a detalle_cuota es automática en el modelo save()
            multa_serializer = MultaSerializer(multa)
            return Response(multa_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MultaDetailAPIView(APIView):
    """Vista para detalle, actualizar y eliminar multas"""
    
    def get(self, request, pk):
        multa = get_object_or_404(Multa, pk=pk)
        serializer = MultaSerializer(multa)
        return Response(serializer.data)

    def patch(self, request, pk):
        multa = get_object_or_404(Multa, pk=pk)
        serializer = MultaSerializer(multa, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        multa = get_object_or_404(Multa, pk=pk)
        multa.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# VISTAS ESPECIALES PARA MULTAS
class MultaConvertirACuotaAPIView(APIView):
    """Vista para forzar conversión de multa a cuota (por si no fue automática)"""
    
    def post(self, request, multa_id):
        multa = get_object_or_404(Multa, pk=multa_id)
        try:
            detalle = multa.convertir_a_detalle_cuota()
            return Response({
                'message': 'Multa convertida a cuota exitosamente',
                'detalle_cuota_id': detalle.id,
                'cuota_id': detalle.cuota.id
            })
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class MultasPorResidenteAPIView(APIView):
    """Vista para obtener multas por residente"""
    
    def get(self, request):
        residente_id = request.query_params.get('residente_id')
        if not residente_id:
            return Response(
                {'error': 'Parámetro residente_id requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        multas = Multa.objects.filter(residente_id=residente_id).order_by('-fecha_creacion')
        serializer = MultaSerializer(multas, many=True)
        return Response(serializer.data)

class MultasPorResidenciaAPIView(APIView):
    """Vista para obtener multas por residencia"""
    
    def get(self, request):
        residencia_id = request.query_params.get('residencia_id')
        if not residencia_id:
            return Response(
                {'error': 'Parámetro residencia_id requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        multas = Multa.objects.filter(residencia_id=residencia_id).order_by('-fecha_creacion')
        serializer = MultaSerializer(multas, many=True)
        return Response(serializer.data)

class MisMultasAPIView(APIView):
    """Vista para que un residente vea SUS multas"""
    
    def get(self, request):
        # Solo residentes pueden ver sus propias multas
        if not hasattr(request.user, 'residente'):
            return Response(
                {'error': 'Acceso denegado'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        residente = request.user.residente
        multas = Multa.objects.filter(residente=residente).order_by('-fecha_creacion')
        serializer = MultaSerializer(multas, many=True)
        return Response(serializer.data)