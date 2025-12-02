from django.urls import path
from . import views

urlpatterns = [
    path('api/crear-pedido/', views.crear_pedido_api, name='crear_pedido_api'),
    path('checkout/<int:pedido_id>/', views.checkout_pedido_view, name='checkout_pedido'),
    
    # ... tus otras urls ...
    path('confirmar-transferencia/<int:pedido_id>/', views.confirmar_transferencia_view, name='confirmar_transferencia'),
    
    # --- AGREGA ESTA LÍNEA NUEVA ---
    path('transferencia-exitosa/<int:pedido_id>/', views.pedido_confirmado_transferencia_view, name='pedido_confirmado_transferencia'),
    
    # ... resto de urls (webhooks, etc) ...
    path('pago/exitoso/', views.pago_exitoso_pedido_view, name='pago_exitoso_pedido'),
    path('pago/pendiente/', views.pago_pendiente_pedido_view, name='pago_pendiente_pedido'),
    path('pago/fallido/', views.pago_fallido_pedido_view, name='pago_fallido_pedido'),
    path('webhook-mp/', views.mercadopago_webhook_view, name='mercadopago_webhook'),
]