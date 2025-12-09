from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from productos.models import Producto

class StaticViewSitemap(Sitemap):
    """Sitemap para páginas estáticas (Inicio, Sobre Mí, etc.)"""
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        # Lista de 'names' de tus URLs estáticas
        return ['inicio', 'sobre_mi', 'servicios', 'lista_productos']

    def location(self, item):
        return reverse(item)

class ProductoSitemap(Sitemap):
    """Sitemap dinámico para todos tus productos"""
    priority = 0.8 # Alta prioridad para Google
    changefreq = 'daily'

    def items(self):
        # Solo productos disponibles
        return Producto.objects.filter(disponible=True)

    def lastmod(self, obj):
        # No tenemos fecha de modificación, usamos algo fijo o nada
        return None