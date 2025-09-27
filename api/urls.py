from django.urls import path, include

urlpatterns = [
    path('api/accounts/', include('accounts.urls')),  # Rutas para la app accounts
    #path('api/propiedades/', include('propiedades.urls')), # Rutas para la app propiedades
    path('api/condominio/', include('condominio.urls')),  # Rutas para la app condominio
    path('api/finance/', include('finance.urls')),  # Rutas para la app finance
    # api/urls.py
]
