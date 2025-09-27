# condominio/admin.py
from django.contrib import admin
from .models import Unidad, Residencia, Habitante

@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'tipo_unidad', 'estado', 'precio_alquiler', 'esta_activa']
    list_filter = ['tipo_unidad', 'estado', 'esta_activa']
    search_fields = ['codigo', 'nombre', 'ubicacion']

@admin.register(Residencia)
class ResidenciaAdmin(admin.ModelAdmin):
    list_display = ['residente', 'unidad', 'tipo_contrato', 'fecha_inicio', 'esta_activa']
    list_filter = ['tipo_contrato', 'esta_activa', 'fecha_inicio']
    search_fields = ['residente__usuario__nombre', 'unidad__codigo']

@admin.register(Habitante)
class HabitanteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'residencia', 'tipo_parentesco', 'es_contacto_emergencia']
    list_filter = ['tipo_parentesco', 'es_contacto_emergencia']
    search_fields = ['nombre', 'apellido', 'ci']
