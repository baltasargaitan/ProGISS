from django.contrib import admin
from django.urls import path, include  # Importa include para enlazar las URLs de la app

urlpatterns = [
    path('admin/', admin.site.urls),            # URL para el panel de administración
    path('', include('gestion_datos.urls')),    # Redirige a las rutas de la app gestion_datos
]
