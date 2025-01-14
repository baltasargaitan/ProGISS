from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # Vista principal
    path('detalle/<int:id>/', views.detalle_afiliado, name='detalle_afiliado'),  # Detalle de un afiliado
    path('segmentacion/', views.segmentacion, name='segmentacion'),  # Vista para segmentación
    path('predicciones_cliente/<int:id>/', views.predicciones_cliente, name='predicciones_cliente'),  # Nueva ruta
    path('hospitalizaciones_proyectadas/', views.hospitalizaciones_proyectadas, name='hospitalizaciones_proyectadas'),

    path('exportar_predicciones/', views.exportar_predicciones, name='exportar_predicciones'),
]
