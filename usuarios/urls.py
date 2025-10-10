from django.urls import path
from . import views
from django.shortcuts import render

urlpatterns = [
    # --- URLS DEL FLUJO DE REGISTRO Y ACTIVACIÓN ---
    # /cuenta/register/ -> Muestra el formulario de registro
    path('register/', views.register_view, name='register'),
    
    # /cuenta/register/done/ -> Página que dice "Revisa tu email"
    path('register/done/', lambda request: render(request, 'usuarios/register_done.html'), name='register_done'),
    
    # /cuenta/activate/<uidb64>/<token>/ -> El enlace mágico del email que activa la cuenta
    path('activate/<uidb64>/<token>/', views.activate_view, name='activate'),
    
    # /cuenta/register/complete/ -> Página que dice "¡Cuenta activada!"
    path('register/complete/', lambda request: render(request, 'usuarios/register_complete.html'), name='register_complete'),
    
    
    # --- URLS DE LOGIN, LOGOUT Y PERFIL (sin cambios) ---
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.profile_view, name='profile'),
]
