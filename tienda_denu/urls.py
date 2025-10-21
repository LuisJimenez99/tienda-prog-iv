from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('', core_views.inicio, name="inicio"),
    path('sobre-mi/', core_views.sobre_mi_view, name='sobre_mi'),
    path('productos/', include('productos.urls')),
    path('cuenta/', include('usuarios.urls')),
    path('turnos/', include('turnos.urls')),
    path('recetas/', include('recetas.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

