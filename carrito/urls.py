from django.urls import path
from . import views
from . import admin_views # <-- 1. IMPORTAR VISTAS DEL ADMIN

urlpatterns = [
    # --- API (Frontend JS) ---
    path('api/crear-pedido/', views.crear_pedido_api, name='crear_pedido_api'),
    
    # --- CHECKOUT Y PAGOS ---
    path('checkout/<int:pedido_id>/', views.checkout_pedido_view, name='checkout_pedido'),
    path('confirmar-transferencia/<int:pedido_id>/', views.confirmar_transferencia_view, name='confirmar_transferencia'),
    path('transferencia-exitosa/<int:pedido_id>/', views.pedido_confirmado_transferencia_view, name='pedido_confirmado_transferencia'),
    
    # --- FEEDBACK DE PAGOS ---
    path('pago/exitoso/', views.pago_exitoso_pedido_view, name='pago_exitoso_pedido'),
    path('pago/pendiente/', views.pago_pendiente_pedido_view, name='pago_pendiente_pedido'),
    path('pago/fallido/', views.pago_fallido_pedido_view, name='pago_fallido_pedido'),
    
    # --- WEBHOOK (CEREBRO) ---
    path('webhook-mp/', views.mercadopago_webhook_view, name='mercadopago_webhook'),

    # --- DASHBOARD ADMIN (NUEVA RUTA) ---
    path('admin/dashboard/', admin_views.dashboard_ventas_view, name='admin_dashboard'),
]