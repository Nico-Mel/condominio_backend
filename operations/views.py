from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Tarea, Aviso, Notificacion
from .serializers import TareaSerializer, TareaCreateSerializer, TomarTareaSerializer, CompletarTareaSerializer
from .serializers import AvisoSerializer, AvisoCreateSerializer, NotificacionSerializer, MarcarLeidaSerializer
class TareaListCreateAPIView(APIView):
    """Vista para listar y crear tareas (solo admin)"""
    
    def get(self, request):
        tareas = Tarea.objects.all()
        serializer = TareaSerializer(tareas, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = TareaCreateSerializer(data=request.data)
        if serializer.is_valid():
            tarea = serializer.save(creado_por=request.user)

            tarea_serializer = TareaSerializer(tarea)
            
            # Aquí después agregarás la notificación push
            # self.enviar_notificacion_tarea(tarea)
            
            return Response(tarea_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TareaDetailAPIView(APIView):
    """Vista para detalle, actualizar y eliminar tareas"""
    
    def get(self, request, pk):
        tarea = get_object_or_404(Tarea, pk=pk)
        serializer = TareaSerializer(tarea)
        return Response(serializer.data)
    
    def patch(self, request, pk):
        tarea = get_object_or_404(Tarea, pk=pk)
        serializer = TareaSerializer(tarea, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        tarea = get_object_or_404(Tarea, pk=pk)
        tarea.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MisTareasAPIView(APIView):
    """Vista para que un usuario vea las tareas que TOMÓ"""
    
    def get(self, request):
        tareas = Tarea.objects.filter(tomada_por=request.user)
        serializer = TareaSerializer(tareas, many=True)
        return Response(serializer.data)

class TareasDisponiblesAPIView(APIView):
    """Vista para que un usuario vea tareas disponibles para su ROL"""
    
    def get(self, request):
        # Tareas pendientes que coinciden con el rol del usuario y NO han sido tomadas
        tareas = Tarea.objects.filter(
            asignado_rol=request.user.rol,
            estado='pendiente',
            tomada_por__isnull=True
        )
        serializer = TareaSerializer(tareas, many=True)
        return Response(serializer.data)

class TomarTareaAPIView(APIView):
    """Vista para que un usuario tome una tarea disponible"""
    
    def post(self, request, tarea_id):
        tarea = get_object_or_404(Tarea, pk=tarea_id)
        serializer = TomarTareaSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                tarea.tomar_tarea(request.user)
                tarea_serializer = TareaSerializer(tarea)
                return Response({
                    'message': 'Tarea tomada exitosamente',
                    'tarea': tarea_serializer.data
                })
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CompletarTareaAPIView(APIView):
    """Vista para marcar tarea como completada"""
    
    def post(self, request, tarea_id):
        tarea = get_object_or_404(Tarea, pk=tarea_id)
        
        # Verificar que el usuario sea quien tomó la tarea
        if tarea.tomada_por != request.user:
            return Response(
                {'error': 'Solo el usuario asignado puede completar esta tarea'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CompletarTareaSerializer(data=request.data)
        if serializer.is_valid():
            tarea.completar_tarea()
            tarea_serializer = TareaSerializer(tarea)
            return Response({
                'message': 'Tarea completada exitosamente',
                'tarea': tarea_serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TareasPorRolAPIView(APIView):
    """Vista para admin: ver tareas por rol específico"""
    
    def get(self, request):
        rol_id = request.query_params.get('rol_id')
        if not rol_id:
            return Response(
                {'error': 'Parámetro rol_id requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tareas = Tarea.objects.filter(asignado_rol_id=rol_id)
        serializer = TareaSerializer(tareas, many=True)
        return Response(serializer.data)

# AVISOS

class AvisoListCreateAPIView(APIView):
    """Vista para listar y crear avisos (admin)"""
    
    def get(self, request):
        avisos = Aviso.objects.filter(es_activo=True)
        serializer = AvisoSerializer(avisos, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = AvisoCreateSerializer(data=request.data)
        if serializer.is_valid():
            aviso = serializer.save(creado_por=request.user)
            
            # Aquí después crearás notificaciones para los usuarios afectados
            # self.crear_notificaciones_aviso(aviso)
            
            aviso_serializer = AvisoSerializer(aviso)
            return Response(aviso_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AvisoDetailAPIView(APIView):
    """Vista para detalle, actualizar y eliminar avisos"""
    
    def get(self, request, pk):
        aviso = get_object_or_404(Aviso, pk=pk)
        serializer = AvisoSerializer(aviso)
        return Response(serializer.data)
    
    def patch(self, request, pk):
        aviso = get_object_or_404(Aviso, pk=pk)
        serializer = AvisoSerializer(aviso, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        aviso = get_object_or_404(Aviso, pk=pk)
        # En lugar de eliminar, desactivamos
        aviso.es_activo = False
        aviso.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AvisosParaMiAPIView(APIView):
    """Vista para que un usuario vea los avisos relevantes para él"""
    
    def get(self, request):
        from django.utils import timezone
        from django.db.models import Q
        
        # Avisos activos que no han expirado
        avisos = Aviso.objects.filter(
            Q(fecha_expiracion__isnull=True) | Q(fecha_expiracion__gte=timezone.now()),
            es_activo=True
        )

        
        # Filtrar avisos relevantes para el usuario
        avisos_relevantes = []
        for aviso in avisos:
            if self.es_aviso_relevante(aviso, request.user):
                avisos_relevantes.append(aviso)
        
        serializer = AvisoSerializer(avisos_relevantes, many=True)
        return Response(serializer.data)
    
    def es_aviso_relevante(self, aviso, usuario):
        """Determina si un aviso es relevante para el usuario"""
        if aviso.para_todos:
            return True
        
        if aviso.para_roles.exists() and usuario.rol in aviso.para_roles.all():
            return True
            
        if (hasattr(usuario, 'residente') and 
            usuario.residente and 
            usuario.residente.residencia in aviso.para_residencias.all()):
            return True
            
        return False

# NOTIFICACIONES

class MisNotificacionesAPIView(APIView):
    """Vista para que un usuario vea SUS notificaciones"""
    
    def get(self, request):
        notificaciones = Notificacion.objects.filter(usuario=request.user)
        serializer = NotificacionSerializer(notificaciones, many=True)
        return Response(serializer.data)

class NotificacionesNoLeidasAPIView(APIView):
    """Vista para notificaciones no leídas del usuario"""
    
    def get(self, request):
        notificaciones = Notificacion.objects.filter(usuario=request.user, leida=False)
        serializer = NotificacionSerializer(notificaciones, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        # Marcar todas como leídas
        Notificacion.objects.filter(usuario=request.user, leida=False).update(
            leida=True, 
            fecha_leida=timezone.now()
        )
        return Response({'message': 'Todas las notificaciones marcadas como leídas'})

class MarcarNotificacionLeidaAPIView(APIView):
    """Vista para marcar una notificación específica como leída"""
    
    def post(self, request, notificacion_id):
        notificacion = get_object_or_404(Notificacion, pk=notificacion_id, usuario=request.user)
        serializer = MarcarLeidaSerializer(data=request.data)
        
        if serializer.is_valid():
            notificacion.leida = serializer.validated_data['leida']
            notificacion.fecha_leida = timezone.now() if serializer.validated_data['leida'] else None
            notificacion.save()
            
            return Response({'message': 'Notificación actualizada'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)