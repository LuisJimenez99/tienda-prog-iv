from django.urls import path
from . import views

urlpatterns = [
    # /productos/ -> Muestra la lista de todos los productos
    path('', views.lista_productos, name='lista_productos'),
    
    # --- URL NUEVA PARA EL DETALLE DEL PRODUCTO ---
    # /productos/5/ -> Muestra el detalle del producto con ID 5
    # <int:producto_id> captura el número de la URL y lo pasa a la vista.
    path('<int:producto_id>/', views.detalle_producto, name='detalle_producto'),

    # /recetas/api/random/ -> Tu API para recetas aleatorias
    path('api/random/', views.random_receta_api, name='random_receta_api'),
]


