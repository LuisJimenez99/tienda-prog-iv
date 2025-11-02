# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('sobre-mi/', views.sobre_mi_view, name='sobre_mi'),
    path('servicios/', views.servicios_view, name='servicios'),
    path('comprar-recetario/', views.checkout_recetario_view, name='checkout_recetario'),
]