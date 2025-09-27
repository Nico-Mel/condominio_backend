# condominio/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Unidad, Residencia, Habitante, AreaComun, ReservaAreaComun
from .serializers import UnidadSerializer, ResidenciaSerializer, HabitanteSerializer
from .serializers import HabitanteCreateSerializer, AreaComunSerializer
from .serializers import ReservaAreaComunSerializer, ReservaAreaComunCreateSerializer, ReservaAreaComunUpdateSerializer
# Unidad Views
class UnidadListCreateAPIView(APIView):
    def get(self, request):
        unidades = Unidad.objects.all()
        
        # FILTROS
        edificio = request.GET.get('edificio')
        if edificio:
            unidades = unidades.filter(edificio__icontains=edificio)
            
        tipo_unidad = request.GET.get('tipo_unidad')
        if tipo_unidad:
            unidades = unidades.filter(tipo_unidad=tipo_unidad)
            
        piso = request.GET.get('piso')
        if piso:
            unidades = unidades.filter(piso=piso)
            
        estado = request.GET.get('estado')
        if estado:
            unidades = unidades.filter(estado=estado)
            
        esta_activa = request.GET.get('esta_activa')
        if esta_activa is not None:
            esta_activa = esta_activa.lower() in ['true', '1', 'yes']
            unidades = unidades.filter(esta_activa=esta_activa)
        
        # Búsqueda por código o nombre
        search = request.GET.get('search')
        if search:
            unidades = unidades.filter(
                Q(codigo__icontains=search) | 
                Q(nombre__icontains=search) |
                Q(edificio__icontains=search)
            )
        
        serializer = UnidadSerializer(unidades, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UnidadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UnidadDetailAPIView(APIView):
    def get(self, request, pk):
        unidad = get_object_or_404(Unidad, pk=pk)
        serializer = UnidadSerializer(unidad)
        return Response(serializer.data)

    def patch(self, request, pk):
        unidad = get_object_or_404(Unidad, pk=pk)
        serializer = UnidadSerializer(unidad, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """HARD DELETE - Eliminación permanente"""
        unidad = get_object_or_404(Unidad, pk=pk)
        
        # Verificar si tiene residencias activas
        residencias_activas = unidad.residencias.filter(esta_activa=True)
        if residencias_activas.exists():
            return Response(
                {"error": "No se puede eliminar una unidad con residencias activas. Desactive las residencias primero."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        unidad.delete()
        return Response(
            {"message": f"Unidad {unidad.codigo} eliminada permanentemente"},
            status=status.HTTP_204_NO_CONTENT
        )

class UnidadToggleActivaAPIView(APIView):
    """SOFT DELETE - Toggle para activar/desactivar unidad"""
    def patch(self, request, pk):
        unidad = get_object_or_404(Unidad, pk=pk)
        
        # Si vamos a desactivar, verificar residencias activas
        if unidad.esta_activa:
            residencias_activas = unidad.residencias.filter(esta_activa=True)
            if residencias_activas.exists():
                return Response(
                    {"error": "No se puede desactivar una unidad con residencias activas. Desactive las residencias primero."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        unidad.esta_activa = not unidad.esta_activa
        unidad.save()
        
        # Si se desactiva la unidad, también desactivar residencias asociadas
        if not unidad.esta_activa:
            unidad.residencias.update(esta_activa=False)
        
        return Response({
            "id": unidad.id,
            "codigo": unidad.codigo,
            "esta_activa": unidad.esta_activa,
            "message": f"Unidad {unidad.codigo} {'activada' if unidad.esta_activa else 'desactivada'}"
        })

class UnidadHardDeleteAPIView(APIView):
    """HARD DELETE forzado - Elimina incluso con residencias (PELIGROSO)"""
    def delete(self, request, pk):
        unidad = get_object_or_404(Unidad, pk=pk)
        
        # Eliminar en cascada (residencias y habitantes)
        codigo_unidad = unidad.codigo
        unidad.delete()
        
        return Response(
            {"message": f"Unidad {codigo_unidad} y todas sus residencias/habitantes eliminados permanentemente"},
            status=status.HTTP_204_NO_CONTENT
        )

# Residencia Views (mantener las existentes y agregar toggles)
class ResidenciaListCreateAPIView(APIView):
    def get(self, request):
        residencias = Residencia.objects.all()
        serializer = ResidenciaSerializer(residencias, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ResidenciaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResidenciaDetailAPIView(APIView):
    def get(self, request, pk):
        residencia = get_object_or_404(Residencia, pk=pk)
        serializer = ResidenciaSerializer(residencia)
        return Response(serializer.data)

    def patch(self, request, pk):
        residencia = get_object_or_404(Residencia, pk=pk)
        serializer = ResidenciaSerializer(residencia, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """HARD DELETE Residencia"""
        residencia = get_object_or_404(Residencia, pk=pk)
        residencia.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ResidenciaToggleActivaAPIView(APIView):
    def patch(self, request, pk):
        residencia = get_object_or_404(Residencia, pk=pk)
        residencia.esta_activa = not residencia.esta_activa
        residencia.save()
        
        # Actualizar estado de la unidad
        unidad = residencia.unidad
        if residencia.esta_activa:
            unidad.estado = 'ocupada'
        else:
            # Verificar si hay otras residencias activas
            otras_activas = unidad.residencias.filter(esta_activa=True).exclude(id=residencia.id)
            if not otras_activas.exists():
                unidad.estado = 'disponible'
        unidad.save()
        
        return Response({
            "id": residencia.id,
            "esta_activa": residencia.esta_activa,
            "unidad_estado": unidad.estado,
            "message": f"Residencia {'activada' if residencia.esta_activa else 'desactivada'}"
        })

# Habitante Views
class HabitanteDetailAPIView(APIView):
    def get(self, request, residencia_id, pk):
        habitante = get_object_or_404(Habitante, pk=pk, residencia_id=residencia_id)
        serializer = HabitanteSerializer(habitante)
        return Response(serializer.data)

    def patch(self, request, residencia_id, pk):
        habitante = get_object_or_404(Habitante, pk=pk, residencia_id=residencia_id)
        serializer = HabitanteCreateSerializer(habitante, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, residencia_id, pk):
        habitante = get_object_or_404(Habitante, pk=pk, residencia_id=residencia_id)
        habitante.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class HabitanteToggleActivaAPIView(APIView):
    def patch(self, request, residencia_id, pk):
        habitante = get_object_or_404(Habitante, pk=pk, residencia_id=residencia_id)
        habitante.esta_activo = not habitante.esta_activo
        habitante.save()

        residencia = getattr(habitante, 'residencia', None)
        unidad = getattr(residencia, 'unidad', None) if residencia else None
        unidad_estado = getattr(unidad, 'estado', None) if unidad else None

        return Response({
            "id": habitante.id,
            "esta_activa": habitante.esta_activo,
            "residencia_id": residencia.id if residencia else None,
            "unidad_id": unidad.id if unidad else None,
            "unidad_estado": unidad_estado,
            "message": f"Habitante {'activado' if habitante.esta_activo else 'desactivado'}"
        })
# Views específicas para relaciones
class ResidenciaHabitantesListAPIView(APIView):
    def get(self, request, residencia_id):
        residencia = get_object_or_404(Residencia, pk=residencia_id)
        habitantes = residencia.habitantes.all()
        serializer = HabitanteSerializer(habitantes, many=True)
        return Response(serializer.data)

    def post(self, request, residencia_id):
        residencia = get_object_or_404(Residencia, pk=residencia_id)
        data = request.data.copy()
        data['residencia'] = residencia.id
        data['residente_titular'] = residencia.residente.id
        
        serializer = HabitanteCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UnidadResidenciasListAPIView(APIView):
    def get(self, request, unidad_id):
        unidad = get_object_or_404(Unidad, pk=unidad_id)
        residencias = unidad.residencias.all()
        serializer = ResidenciaSerializer(residencias, many=True)
        return Response(serializer.data)
    
# condominio/views.py (agregar al final)
class AreaComunListCreateAPIView(APIView):
    def get(self, request):
        areas = AreaComun.objects.filter(esta_activa=True)
        serializer = AreaComunSerializer(areas, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AreaComunSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AreaComunDetailAPIView(APIView):
    def get(self, request, pk):
        area = get_object_or_404(AreaComun, pk=pk)
        serializer = AreaComunSerializer(area)
        return Response(serializer.data)

    def patch(self, request, pk):
        area = get_object_or_404(AreaComun, pk=pk)
        serializer = AreaComunSerializer(area, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# condominio/views.py (actualizar las views de reservas)
class ReservaAreaComunListCreateAPIView(APIView):
    def get(self, request):
        # Si es residente, solo ver sus reservas
        if hasattr(request.user, 'residente'):
            reservas = ReservaAreaComun.objects.filter(residente=request.user.residente)
        else:
            # Si es admin, ver todas las reservas
            reservas = ReservaAreaComun.objects.all()
        
        # Filtros adicionales
        fecha = request.GET.get('fecha')
        if fecha:
            reservas = reservas.filter(fecha=fecha)
            
        estado = request.GET.get('estado')
        if estado:
            reservas = reservas.filter(estado=estado)
            
        area_comun_id = request.GET.get('area_comun')
        if area_comun_id:
            reservas = reservas.filter(area_comun_id=area_comun_id)
        
        serializer = ReservaAreaComunSerializer(reservas, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Verificar que el usuario sea residente
        if not hasattr(request.user, 'residente'):
            return Response(
                {"error": "Solo los residentes pueden hacer reservas"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ReservaAreaComunCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Crear reserva con estado pendiente inicialmente
            reserva = serializer.save(
                residente=request.user.residente,
                estado='pendiente'  # Estado inicial
            )
            
            # Serializer completo para la respuesta
            reserva_serializer = ReservaAreaComunSerializer(reserva)
            return Response(reserva_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ReservaAreaComunDetailAPIView(APIView):
    def get(self, request, pk):
        reserva = get_object_or_404(ReservaAreaComun, pk=pk)
        
        # Verificar permisos: residente solo puede ver sus propias reservas
        if hasattr(request.user, 'residente') and reserva.residente != request.user.residente:
            return Response(
                {"error": "No tienes permisos para ver esta reserva"}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = ReservaAreaComunSerializer(reserva)
        return Response(serializer.data)

    def patch(self, request, pk):
        reserva = get_object_or_404(ReservaAreaComun, pk=pk)
        
        # Verificar permisos
        if hasattr(request.user, 'residente') and reserva.residente != request.user.residente:
            return Response(
                {"error": "No tienes permisos para modificar esta reserva"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Si es residente, solo permitir cancelar
        if hasattr(request.user, 'residente'):
            if 'estado' in request.data and request.data['estado'] != 'cancelada':
                return Response(
                    {"error": "Solo puedes cancelar tus reservas"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = ReservaAreaComunUpdateSerializer(reserva, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # Si se confirma la reserva, crear la cuota automáticamente
            if 'estado' in request.data and request.data['estado'] == 'reservada':
                reserva.crear_cuota_reserva()
            
            return Response(ReservaAreaComunSerializer(reserva).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ConfirmarReservaAPIView(APIView):
    """Endpoint específico para confirmar reservas (admin only)"""
    def post(self, request, pk):
        # Verificar que el usuario es admin/staff
        
        reserva = get_object_or_404(ReservaAreaComun, pk=pk)
        
        if reserva.estado != 'pendiente':
            return Response(
                {"error": f"La reserva ya está {reserva.get_estado_display()}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reserva.estado = 'reservada'
        reserva.save()
        
        # La cuota se crea automáticamente en el save() del modelo
        serializer = ReservaAreaComunSerializer(reserva)
        return Response(serializer.data)

class CancelarReservaAPIView(APIView):
    """Endpoint para cancelar reservas"""
    def post(self, request, pk):
        reserva = get_object_or_404(ReservaAreaComun, pk=pk)
        
        # Verificar permisos: residente solo puede cancelar sus propias reservas
        if hasattr(request.user, 'residente') and reserva.residente != request.user.residente:
            return Response(
                {"error": "No tienes permisos para cancelar esta reserva"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if reserva.estado in ['cancelada', 'completada']:
            return Response(
                {"error": f"La reserva ya está {reserva.get_estado_display()}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reserva.estado = 'cancelada'
        reserva.save()
        
        # La cuota se cancela automáticamente en el save() del modelo
        serializer = ReservaAreaComunSerializer(reserva)
        return Response(serializer.data)