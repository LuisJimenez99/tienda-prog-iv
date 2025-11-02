from django.contrib import admin, messages
from .models import Pedido, ItemPedido
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import format_html
from .views import reponer_stock
from pynliner import Pynliner
from configuracion.models import AparienciaConfig

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    readonly_fields = ('producto_link', 'cantidad', 'precio_unitario', 'get_costo')
    fields = ('producto_link', 'cantidad', 'precio_unitario', 'get_costo')
    can_delete = False
    extra = 0
    
    def get_costo(self, obj):
        if obj.precio_unitario is not None and obj.cantidad is not None:
            return obj.precio_unitario * obj.cantidad
        return 0
    get_costo.short_description = "Subtotal"

    def producto_link(self, obj):
        if obj.producto:
            from django.urls import reverse
            url = reverse('admin:productos_producto_change', args=[obj.producto.id])
            return format_html('<a href="{}">{}</a>', url, obj.producto.nombre)
        return "Producto eliminado"
    producto_link.short_description = "Producto"


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_creacion', 'total', 'estado', 'codigo_seguimiento')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('cliente__username', 'id')
    
    # --- LÍNEA CLAVE AÑADIDA AQUÍ ---
    list_editable = ['estado'] # <-- Hacemos el estado editable desde la lista
    
    readonly_fields = ('id', 'cliente', 'fecha_creacion', 'total', 'direccion_envio', 'ciudad_envio', 'codigo_postal_envio', 'telefono_contacto')
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('id', 'cliente', 'fecha_creacion', 'total')
        }),
        ('Estado y Seguimiento (Tu Gestión)', {
            'fields': ('estado', 'metodo_envio_elegido', 'codigo_seguimiento')
        }),
        ('Datos de Envío (Cliente)', {
            'fields': ('direccion_envio', 'ciudad_envio', 'codigo_postal_envio', 'telefono_contacto')
        }),
    )
    
    inlines = [ItemPedidoInline]
    
    actions = ['marcar_cancelado_y_reponer_stock']

    @admin.action(description='Cancelar pedidos y reponer stock (para transferencias fallidas)')
    def marcar_cancelado_y_reponer_stock(self, request, queryset):
        pedidos_actualizados = 0
        for pedido in queryset.filter(estado='pendiente_transferencia'):
            if reponer_stock(pedido):
                pedido.estado = 'cancelado'
                pedido.save()
                pedidos_actualizados += 1
        
        if pedidos_actualizados > 0:
            self.message_user(request, 
                f'{pedidos_actualizados} pedidos han sido cancelados y el stock ha sido repuesto.', 
                messages.SUCCESS)
        else:
            self.message_user(request, 
                'No se pudo reponer stock. Solo aplica a pedidos "pendiente_transferencia".', 
                messages.WARNING)
    
    def save_model(self, request, obj, form, change):
        old_codigo_seguimiento = ""
        if change:
            try:
                old_codigo_seguimiento = Pedido.objects.get(pk=obj.pk).codigo_seguimiento or ""
            except Pedido.DoesNotExist:
                pass
        
        super().save_model(request, obj, form, change)
        
        new_codigo_seguimiento = obj.codigo_seguimiento or ""

        # Lógica para enviar email cuando se añade código de seguimiento
        if new_codigo_seguimiento != old_codigo_seguimiento and new_codigo_seguimiento != "":
            try:
                # 1. Obtenemos la configuración de apariencia (para el logo y colores)
                apariencia_config = AparienciaConfig.objects.first()

                subject = f"¡Tu pedido #{obj.id} ha sido despachado!"
                context = {
                    'pedido': obj, 
                    'cliente': obj.cliente,
                    'apariencia_config': apariencia_config # <-- La pasamos a la plantilla
                }

                # 2. Renderizamos la plantilla .txt (como fallback)
                message_txt = render_to_string('carrito/email/envio_despachado.txt', context)
                
                # 3. Renderizamos la plantilla .html
                message_html = render_to_string('carrito/email/envio_despachado.html', context)
                
                # 4. Usamos el "inliner" para aplicar el CSS
                p = Pynliner()
                message_html_inlined = p.from_string(message_html).run()

                # 5. Enviamos el email
                send_mail(
                    subject, 
                    message_txt, # Fallback de texto plano
                    settings.DEFAULT_FROM_EMAIL, 
                    [obj.cliente.email],
                    html_message=message_html_inlined # <-- ¡El HTML va aquí!
                )
                
                if obj.estado != 'despachado':
                    obj.estado = 'despachado'
                    obj.save()
                
                self.message_user(request, "Código de seguimiento guardado y email HTML enviado al cliente.")
            
            except Exception as e:
                self.message_user(request, f"Error al enviar el email: {e}", level='ERROR')
