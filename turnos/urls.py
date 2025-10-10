from django.urls import path
from . import views

urlpatterns = [
    # --- URLs que ya tenías ---
    # /turnos/ -> Muestra el calendario principal
    path('', views.calendario_view, name='calendario'),
    
    # /turnos/api/horarios/... -> El API que devuelve los horarios disponibles
    path('api/horarios/<str:date_str>/', views.horarios_disponibles_api, name='horarios_api'),
    
    
    # --- URLS NUEVAS PARA EL PROCESO DE PAGO ---
    # /turnos/checkout/ -> Página para confirmar y ver los métodos de pago
    path('checkout/', views.checkout_turno_view, name='checkout_turno'),
    
    # /turnos/confirmar-reserva/ -> Página final que guarda el turno y envía los emails
    path('confirmar-reserva/', views.confirmar_reserva_view, name='confirmar_reserva'),

# /turnos/ -> Muestra el calendario principal
path('', views.calendario_view, name='calendario'),
    
    # /turnos/api/horarios/... -> El API que devuelve los horarios disponibles
path('api/horarios/<str:date_str>/', views.horarios_disponibles_api, name='horarios_api'),

    # /turnos/checkout/ -> Página para confirmar y ver los métodos de pago
path('checkout/', views.checkout_turno_view, name='checkout_turno'),

    # /turnos/confirmar-reserva/ -> Acción para confirmar una reserva por transferencia
path('confirmar-reserva/', views.confirmar_reserva_view, name='confirmar_reserva'),


    # --- URLS NUEVAS PARA EL FEEDBACK DE MERCADO PAGO ---
    # /turnos/pago/exitoso/ -> Página que se muestra si el pago fue aprobado
path('pago/exitoso/', views.pago_exitoso_view, name='pago_exitoso'),
    
    # /turnos/pago/pendiente/ -> Página para pagos en efectivo (Rapipago, etc.)
path('pago/pendiente/', views.pago_pendiente_view, name='pago_pendiente'),
    
    # /turnos/pago/fallido/ -> Página si el pago fue rechazado
path('pago/fallido/', views.pago_fallido_view, name='pago_fallido'),
]
