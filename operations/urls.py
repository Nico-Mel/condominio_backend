from django.urls import path
from . import views

urlpatterns = [
    # Tareas generales (admin)
    path('tareas/', views.TareaListCreateAPIView.as_view(), name='tarea-list-create'),
    path('tareas/<int:pk>/', views.TareaDetailAPIView.as_view(), name='tarea-detail'),
    
    # Tareas para usuarios
    path('mis-tareas/', views.MisTareasAPIView.as_view(), name='mis-tareas'),
    path('tareas-disponibles/', views.TareasDisponiblesAPIView.as_view(), name='tareas-disponibles'),
    path('tareas/<int:tarea_id>/tomar/', views.TomarTareaAPIView.as_view(), name='tomar-tarea'),
    path('tareas/<int:tarea_id>/completar/', views.CompletarTareaAPIView.as_view(), name='completar-tarea'),
    
    # Admin
    path('tareas-por-rol/', views.TareasPorRolAPIView.as_view(), name='tareas-por-rol'),
     # Avisos
    path('avisos/', views.AvisoListCreateAPIView.as_view(), name='aviso-list-create'),
    path('avisos/<int:pk>/', views.AvisoDetailAPIView.as_view(), name='aviso-detail'),
    path('avisos-para-mi/', views.AvisosParaMiAPIView.as_view(), name='avisos-para-mi'),
    
    # Notificaciones
    path('mis-notificaciones/', views.MisNotificacionesAPIView.as_view(), name='mis-notificaciones'),
    path('notificaciones-no-leidas/', views.NotificacionesNoLeidasAPIView.as_view(), name='notificaciones-no-leidas'),
    path('notificaciones/<int:notificacion_id>/marcar-leida/', views.MarcarNotificacionLeidaAPIView.as_view(), name='marcar-notificacion-leida'),
]