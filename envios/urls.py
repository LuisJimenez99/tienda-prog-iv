from django.urls import path
from . import views

urlpatterns = [
    path('api/calcular-envio/', views.calcular_envio_api, name='calcular_envio_api'),
]