from django.urls import path
from . import views

urlpatterns = [
    # 1. Pantalla principal del calendario (Donde el usuario elige fecha)
    path('', views.calendario_view, name='calendario'),
    
    # 2. API para obtener horarios (AJAX - Consumida por JS)
    # Ejemplo de uso: /turnos/api/horarios/?fecha=2025-12-10
    path('api/horarios/', views.horarios_disponibles_api, name='api_horarios'),
    
    # 3. Acción de reservar (Procesa el formulario y crea el turno)
    path('reservar/', views.reservar_turno, name='reservar_turno'),
    
    # 4. Pantalla de pago (El paso final antes de Mercado Pago)
    path('checkout/<int:turno_id>/', views.checkout_turno_view, name='checkout_turno'),

    # 5. Confirmación por Transferencia (¡NUEVA RUTA!)
    path('confirmar-transferencia/<int:turno_id>/', views.confirmar_transferencia_turno_view, name='confirmar_transferencia_turno'),

    # 6. Retornos de Mercado Pago (Feedback al usuario)
    path('pago/exitoso/', views.pago_exitoso_view, name='pago_exitoso'),   # <--- Debe llamarse así
    path('pago/pendiente/', views.pago_pendiente_view, name='pago_pendiente'), # <--- Debe llamarse así
    path('pago/fallido/', views.pago_fallido_view, name='pago_fallido'),     # <--- Debe llamarse así
]