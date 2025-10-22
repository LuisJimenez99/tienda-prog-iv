from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.lista_productos, name='lista_productos'),
    path('<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('api/live-search/', views.live_search_api, name='live_search_api'),  
    
]


