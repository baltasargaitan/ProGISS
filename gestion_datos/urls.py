from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),  # Vista principal
    path('dashboard/', views.dashboard, name='dashboard'),  # Vista principal
    path('detalle/<int:id>/', views.detalle_afiliado, name='detalle_afiliado'),  # Detalle de un afiliado
    path('segmentacion/', views.segmentacion, name='segmentacion'),  # Vista para segmentación
    path('predicciones_cliente/<int:id>/', views.predicciones_cliente, name='predicciones_cliente'),  # Predicciones de un cliente específico
    path('hospitalizaciones_proyectadas/', views.hospitalizaciones_proyectadas, name='hospitalizaciones_proyectadas'),
    path('costos_medicos/', views.costos_medicos_proyectados, name='costos_medicos'),
    path('exportar_predicciones/', views.exportar_predicciones, name='exportar_predicciones'),
    path('costos_totales_proyectados/', views.costos_totales_proyectados, name='costos_totales_proyectados'),
    path('proyeccion_estudios/', views.proyeccion_estudios, name='proyeccion_estudios'),  # Ruta para las proyecciones de estudios
    path('error/', views.error_view, name='error'),
]
