from django.urls import path
from . import views

urlpatterns = [
    # 1. Pantalla principal del calendario (Donde el usuario elige fecha)
    path('', views.calendario_view, name='calendario'),
    
    # 2. API para obtener horarios (AJAX - Consumida por JS)
    path('api/horarios/', views.horarios_disponibles_api, name='api_horarios'),
    
    # 3. Acción de reservar (ESTA ES LA QUE TE FALTABA O ESTABA ROTA)
    path('reservar/', views.reservar_turno, name='reservar_turno'),
    
    # 4. Pantalla de pago
    path('checkout/<int:turno_id>/', views.checkout_turno_view, name='checkout_turno'),

    # 5. Confirmación por Transferencia
    path('confirmar-transferencia/<int:turno_id>/', views.confirmar_transferencia_turno_view, name='confirmar_transferencia_turno'),

    # 6. Retornos de Mercado Pago (Feedback al usuario)
    path('pago/exitoso/', views.pago_exitoso_view, name='pago_exitoso'),
    path('pago/pendiente/', views.pago_pendiente_view, name='pago_pendiente'),
    path('pago/fallido/', views.pago_fallido_view, name='pago_fallido'),
]