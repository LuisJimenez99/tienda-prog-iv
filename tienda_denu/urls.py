from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap 
from django.http import HttpResponse
from core.sitemaps import StaticViewSitemap, ProductoSitemap

# Diccionario de sitemaps
sitemaps = {
    'static': StaticViewSitemap,
    'productos': ProductoSitemap,
}

# Vista simple para robots.txt
def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Disallow: /admin/",
        "Disallow: /carrito/",
        "Disallow: /mi-cuenta/",
        "Disallow: /panel/", # <-- Importante: Ocultar el panel de los robots
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('productos/', include('productos.urls')),
    path('turnos/', include('turnos.urls')),
    path('recetas/', include('recetas.urls')),
    path('carrito/', include('carrito.urls')),
    path('envios/', include('envios.urls')),
    path('accounts/', include('allauth.urls')),
    path('mi-cuenta/', include('usuarios.urls')),
    
    # --- RUTA DEL PANEL DE GESTIÓN (NUEVA) ---
    path('panel/', include('panel_gestor.urls')),
    
    # --- RUTAS DE DASHBOARD ADMIN (Antiguo) ---
    path('admin/configuracion/', include('configuracion.admin_urls')), 
    
    # --- RUTAS DE SEO ---
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)