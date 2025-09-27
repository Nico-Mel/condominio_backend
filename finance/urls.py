from django.urls import path
from .views import (
    ExpensaListCreateAPIView, ExpensaDetailAPIView,
    DetalleCuotaListCreateAPIView, DetalleCuotaDetailAPIView,
    CuotaListCreateAPIView, CuotaDetailAPIView,
    PagoListCreateAPIView, PagoDetailAPIView,
    MisCuotasAPIView, MisPagosAPIView, RealizarPagoAPIView,
    CuotasPorResidenteAPIView, CuotasPorPeriodoAPIView, GenerarCuotasMensualesAPIView,
    MultaListCreateAPIView, MultaDetailAPIView, MultaConvertirACuotaAPIView,
    MultasPorResidenteAPIView, MultasPorResidenciaAPIView, MisMultasAPIView
)

urlpatterns = [
    # Expensas
    path('expensas/', ExpensaListCreateAPIView.as_view(), name='expensa-list-create'),
    path('expensas/<int:pk>/', ExpensaDetailAPIView.as_view(), name='expensa-detail'),
    
    # Detalles de Cuota
    path('detalles-cuota/', DetalleCuotaListCreateAPIView.as_view(), name='detalle-cuota-list-create'),
    path('detalles-cuota/<int:pk>/', DetalleCuotaDetailAPIView.as_view(), name='detalle-cuota-detail'),
    
    # Cuotas
    path('cuotas/', CuotaListCreateAPIView.as_view(), name='cuota-list-create'),
    path('cuotas/<int:pk>/', CuotaDetailAPIView.as_view(), name='cuota-detail'),
    
    # Pagos
    path('pagos/', PagoListCreateAPIView.as_view(), name='pago-list-create'),
    path('pagos/<int:pk>/', PagoDetailAPIView.as_view(), name='pago-detail'),
    
    # Vistas residentes
    path('mis-cuotas/', MisCuotasAPIView.as_view(), name='mis-cuotas'),
    path('mis-pagos/', MisPagosAPIView.as_view(), name='mis-pagos'),
    path('realizar-pago/', RealizarPagoAPIView.as_view(), name='realizar-pago'),
    
    # Vistas adicionales
    path('cuotas/residente/<uuid:residente_id>/', CuotasPorResidenteAPIView.as_view(), name='cuotas-por-residente'),
    path('cuotas/periodo/<str:periodo>/', CuotasPorPeriodoAPIView.as_view(), name='cuotas-por-periodo'),
    path('cuotas/generar-mensuales/', GenerarCuotasMensualesAPIView.as_view(), name='generar-cuotas-mensuales'),

    path('multas/', MultaListCreateAPIView.as_view(), name='multa-list-create'),
    path('multas/<int:pk>/', MultaDetailAPIView.as_view(), name='multa-detail'),
    path('multas/<int:multa_id>/convertir/', MultaConvertirACuotaAPIView.as_view(), name='multa-convertir'),
    path('multas/por-residente/', MultasPorResidenteAPIView.as_view(), name='multas-por-residente'),
    path('multas/por-residencia/', MultasPorResidenciaAPIView.as_view(), name='multas-por-residencia'),
    path('mis-multas/', MisMultasAPIView.as_view(), name='mis-multas'),
]