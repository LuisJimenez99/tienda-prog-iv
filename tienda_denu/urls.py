from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views # Asegúrate de que esta línea esté presente

urlpatterns = [
    # URLs que ya tenías
    path('admin/', admin.site.urls),
    path('', core_views.inicio, name="inicio"),
    
    # --- LÍNEA NUEVA AQUÍ ---
    # Esto le dice a Django: "Cuando alguien visite la URL '/sobre-mi/',
    # ejecuta la función 'sobre_mi_view' que está en core/views.py".
    path('sobre-mi/', core_views.sobre_mi_view, name='sobre_mi'),
    
    # El resto de tus URLs
    path('productos/', include('productos.urls')),
    path('cuenta/', include('usuarios.urls')),
    path('turnos/', include('turnos.urls')),
]

# Esto se queda igual, para manejar los archivos de imágenes
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

