from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.inicio, name="inicio"),
    path('sobre-mi/', core_views.sobre_mi_view, name='sobre_mi'),
    
    # Apps principales
    path('productos/', include('productos.urls')),
    path('turnos/', include('turnos.urls')),
    path('recetas/', include('recetas.urls')),
    path('carrito/', include('carrito.urls')),

    # --- LÍNEA NUEVA AQUÍ ---
    # Le decimos a Django que cualquier URL que empiece con 'envios/'
    # debe ser manejada por el archivo 'envios/urls.py'
    path('envios/', include('envios.urls')),

    # Autenticación (allauth)
    path('accounts/', include('allauth.urls')),
    
    # Perfil de usuario personalizado
    path('mi-cuenta/', include('usuarios.urls')),
]

# Servir archivos estáticos y multimedia en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

