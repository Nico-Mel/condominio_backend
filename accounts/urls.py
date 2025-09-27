# accounts/urls.py
from django.urls import path
from .views import (
    RolListCreateAPIView, RolDetailAPIView,
    PermisoListCreateAPIView, PermisoDetailAPIView,
    RolPermisoListCreateAPIView, RolPermisoDetailAPIView,
    UsuarioListCreateAPIView, UsuarioDetailAPIView, UsuarioToggleActivoAPIView,
    LoginView, ResidenteListCreateAPIView, ResidenteDetailAPIView
)

urlpatterns = [
    # Rol
    path('roles/', RolListCreateAPIView.as_view(), name='rol-list-create'),
    path('roles/<uuid:pk>/', RolDetailAPIView.as_view(), name='rol-detail'),

    # Permiso
    path('permisos/', PermisoListCreateAPIView.as_view(), name='permiso-list-create'),
    path('permisos/<uuid:pk>/', PermisoDetailAPIView.as_view(), name='permiso-detail'),

    # RolPermiso
    path('rolpermisos/', RolPermisoListCreateAPIView.as_view(), name='rolpermiso-list-create'),
    path('rolpermisos/<uuid:pk>/', RolPermisoDetailAPIView.as_view(), name='rolpermiso-detail'),

    # Usuario
    path('usuarios/', UsuarioListCreateAPIView.as_view(), name='usuario-list-create'),
    path('usuarios/<uuid:pk>/', UsuarioDetailAPIView.as_view(), name='usuario-detail'),
    path('usuarios/<uuid:pk>/toggle-activo/', UsuarioToggleActivoAPIView.as_view(), name='usuario-toggle-activo'),
    # Login
    path('login/', LoginView.as_view(), name='login'),

    path('residentes/', ResidenteListCreateAPIView.as_view(), name='residente-list-create'),
    path('residentes/<uuid:pk>/', ResidenteDetailAPIView.as_view(), name='residente-detail'),

]
