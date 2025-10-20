from django.urls import path
from . import views

# La lista de URLs debe definirse una sola vez, sin repeticiones.
urlpatterns = [
    # --- URLS DEL CALENDARIO ---
    path('', views.calendario_view, name='calendario'),
    path('api/horarios/<str:date_str>/', views.horarios_disponibles_api, name='horarios_api'),
    
    # --- URLS DEL FLUJO DE PAGO Y RESERVA ---
    path('checkout/', views.checkout_turno_view, name='checkout_turno'),
    path('confirmar-reserva/', views.confirmar_reserva_view, name='confirmar_reserva'),

    # --- URLS DE RESPUESTA DE MERCADO PAGO ---
    path('pago/exitoso/', views.pago_exitoso_view, name='pago_exitoso'),
    path('pago/pendiente/', views.pago_pendiente_view, name='pago_pendiente'),
    path('pago/fallido/', views.pago_fallido_view, name='pago_fallido'),
]

