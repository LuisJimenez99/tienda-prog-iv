from django.urls import path
from . import views

urlpatterns = [
    # /productos/ -> Muestra la lista de todos los productos
    path('', views.lista_productos, name='lista_productos'),
    
    # /productos/5/ -> Muestra el detalle del producto con ID 5
    path('<int:producto_id>/', views.detalle_producto, name='detalle_producto'),

    # /productos/api/live-search/ -> El API para la búsqueda predictiva de productos
    path('api/live-search/', views.live_search_api, name='live_search_api'),

    
    
]


