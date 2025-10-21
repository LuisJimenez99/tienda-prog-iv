from django.urls import path
from . import views

urlpatterns = [
    # Esta línea le dice a Django: "Cuando alguien visite la URL /recetas/api/random/,
    # ejecuta la función 'random_receta_api' que está en el archivo views.py".
    path('api/random/', views.random_receta_api, name='random_receta_api'),
]

