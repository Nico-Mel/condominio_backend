# condominio/urls.py
from django.urls import path
from .views import (
    UnidadListCreateAPIView, UnidadDetailAPIView, UnidadToggleActivaAPIView, UnidadHardDeleteAPIView,
    ResidenciaListCreateAPIView, ResidenciaDetailAPIView, ResidenciaToggleActivaAPIView,
    ResidenciaHabitantesListAPIView, UnidadResidenciasListAPIView,
    HabitanteDetailAPIView, HabitanteToggleActivaAPIView, AreaComunDetailAPIView, 
    AreaComunListCreateAPIView, ReservaAreaComunListCreateAPIView, ReservaAreaComunDetailAPIView,
    CancelarReservaAPIView, ConfirmarReservaAPIView
)

urlpatterns = [
    # Unidades
    path('unidades/', UnidadListCreateAPIView.as_view(), name='unidad-list-create'),  
    # GET: Listar unidades (con filtros)
    # POST: Crear unidad

    path('unidades/<int:pk>/', UnidadDetailAPIView.as_view(), name='unidad-detail'),  
    # GET: Detalle de unidad
    # PATCH: Actualizar unidad
    # DELETE: Eliminar unidad (hard delete, solo si no tiene residencias activas)

    path('unidades/<int:pk>/toggle-activa/', UnidadToggleActivaAPIView.as_view(), name='unidad-toggle-activa'),  
    # PATCH: Activar/desactivar unidad (soft delete)

    path('unidades/<int:pk>/hard-delete/', UnidadHardDeleteAPIView.as_view(), name='unidad-hard-delete'),  
    # DELETE: Eliminar unidad y todas sus residencias/habitantes (forzado)

    # Residencias
    path('residencias/', ResidenciaListCreateAPIView.as_view(), name='residencia-list-create'),  
    # GET: Listar residencias
    # POST: Crear residencia

    path('residencias/<int:pk>/', ResidenciaDetailAPIView.as_view(), name='residencia-detail'),  
    # GET: Detalle de residencia
    # PATCH: Actualizar residencia
    # DELETE: Eliminar residencia

    path('residencias/<int:pk>/toggle-activa/', ResidenciaToggleActivaAPIView.as_view(), name='residencia-toggle-activa'),  
    # PATCH: Activar/desactivar residencia (soft delete)

    # Habitantes
    path('residencias/<int:residencia_id>/habitantes/', ResidenciaHabitantesListAPIView.as_view(), name='residencia-habitantes'),  
    # GET: Listar habitantes de una residencia
    # POST: Crear habitante en una residencia

    path('residencias/<int:residencia_id>/habitantes/<int:pk>/', HabitanteDetailAPIView.as_view(), name='habitante-detail'),  
    # GET: Detalle de habitante
    # PATCH: Actualizar habitante
    # DELETE: Eliminar habitante

    path('residencias/<int:residencia_id>/habitantes/<int:pk>/toggle-activa/', HabitanteToggleActivaAPIView.as_view(), name='habitante-toggle-activa'),  
    # PATCH: Activar/desactivar habitante (soft delete)

    # Relaciones
    path('unidades/<int:unidad_id>/residencias/', UnidadResidenciasListAPIView.as_view(), name='unidad-residencias'),  
    # GET: Listar residencias de una unidad

    # Áreas comunes
    path('areas-comunes/', AreaComunListCreateAPIView.as_view(), name='area-comun-list-create'),  
    # GET: Listar áreas comunes
    # POST: Crear área común

    path('areas-comunes/<int:pk>/', AreaComunDetailAPIView.as_view(), name='area-comun-detail'),  
    # GET: Detalle de área común
    # PATCH: Actualizar área común
    path('reservas/', ReservaAreaComunListCreateAPIView.as_view(), name='reserva-list-create'),
    path('reservas/<int:pk>/', ReservaAreaComunDetailAPIView.as_view(), name='reserva-detail'),
    path('reservas/<int:pk>/confirmar/', ConfirmarReservaAPIView.as_view(), name='reserva-confirmar'),
    path('reservas/<int:pk>/cancelar/', CancelarReservaAPIView.as_view(), name='reserva-cancelar'),
]    
