# tienda_denu/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# from core import views as core_views <-- BORRAMOS ESTA LÍNEA

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- ESTE ES EL CAMBIO PRINCIPAL ---
    # Borramos las líneas de 'inicio' y 'sobre-mi' de aquí
    # y las reemplazamos con este 'include' que carga 
    # todas las URLs de la app 'core' (incluida 'servicios')
    path('', include('core.urls')),
    # --- FIN DEL CAMBIO ---
    
    # Apps principales
    path('productos/', include('productos.urls')),
    path('turnos/', include('turnos.urls')),
    path('recetas/', include('recetas.urls')), # (Tenías esta línea duplicada, quité una)
    path('carrito/', include('carrito.urls')),
    path('envios/', include('envios.urls')),
    path('accounts/', include('allauth.urls')),
    path('mi-cuenta/', include('usuarios.urls')),
    
    # URLs personalizadas del admin (si la tienes)
    path('admin/configuracion/', include('configuracion.admin_urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)