from django.urls import path
from . import views

urlpatterns = [
    # Vistas principales de productos
    path('', views.lista_productos, name='lista_productos'),
    path('<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    
    # --- RUTAS DE FAVORITOS (NUEVAS) ---
    # 1. La página visual donde el usuario ve su lista
    path('mis-favoritos/', views.lista_favoritos, name='lista_favoritos'),
    
    # 2. La API oculta que usa el botón del corazón (AJAX)
    path('api/favorito/<int:producto_id>/', views.toggle_favorito, name='toggle_favorito'),
    
    # --- BUSCADOR ---
    path('api/live-search/', views.live_search_api, name='live_search_api'), 
]