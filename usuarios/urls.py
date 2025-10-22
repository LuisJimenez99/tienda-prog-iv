from django.urls import path
from . import views

urlpatterns = [
    # Esta ruta se encargará de mostrar la página de perfil del usuario.
    # La URL final será: /mi-cuenta/
    path('', views.profile_view, name='profile'),
    
    # Esta es la nueva ruta para la página de edición de perfil.
    # La URL final será: /mi-cuenta/editar/
    path('editar/', views.edit_profile_view, name='edit_profile'),
]