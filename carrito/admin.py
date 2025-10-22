from django.contrib import admin
from .models import Pedido, ItemPedido
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import format_html

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
                subject = f"¡Tu pedido #{obj.id} ha sido despachado!"
                context = {'pedido': obj, 'cliente': obj.cliente}
                message = render_to_string('carrito/email/envio_despachado.txt', context)
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [obj.cliente.email])
                
                if obj.estado != 'despachado':
                    obj.estado = 'despachado'
                    obj.save()
                
                self.message_user(request, "Código de seguimiento guardado y email enviado al cliente.")
            except Exception as e:
                self.message_user(request, f"Error al enviar el email: {e}", level='ERROR')
