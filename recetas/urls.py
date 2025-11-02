from django.urls import path
from . import views

urlpatterns = [
    
    path('recetario/', views.vista_recetario, name='recetario'),
]

