# carrito/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # API para crear el pedido desde el carrito de JS
    path('api/crear-pedido/', views.crear_pedido_api, name='crear_pedido_api'),

    # Página de checkout para un pedido específico
    path('checkout/<int:pedido_id>/', views.checkout_pedido_view, name='checkout_pedido'),
    
    # ¡NUEVA URL! Para el botón de "Confirmar Transferencia"
    path('confirmar-transferencia/<int:pedido_id>/', views.confirmar_transferencia_view, name='confirmar_transferencia'),

    # URLs de feedback de Mercado Pago para pedidos
    path('pago/exitoso/', views.pago_exitoso_pedido_view, name='pago_exitoso_pedido'),
    path('pago/pendiente/', views.pago_pendiente_pedido_view, name='pago_pendiente_pedido'),
    path('pago/fallido/', views.pago_fallido_pedido_view, name='pago_fallido_pedido'),

    # ¡URL DEL WEBHOOK! (Asegúrate de que esta URL exista)
    path('webhook-mp/', views.mercadopago_webhook_view, name='mercadopago_webhook'),
]