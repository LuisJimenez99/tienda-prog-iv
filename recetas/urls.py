from django.urls import path
from . import views

urlpatterns = [
    
    path('api/random/', views.random_receta_api, name='random_receta_api'),
]

