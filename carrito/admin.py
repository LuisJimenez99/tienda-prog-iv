from django.contrib import admin, messages
from .models import Pedido, ItemPedido
from django.utils.html import format_html
from .emails import enviar_email_dinamico  # <-- IMPORTANTE: Importamos la nueva función

# ¡Importamos la función clave desde las vistas!
from .views import descontar_stock


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    readonly_fields = ("producto_link", "cantidad", "precio_unitario", "get_costo")
    fields = ("producto_link", "cantidad", "precio_unitario", "get_costo")
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

            url = reverse("admin:productos_producto_change", args=[obj.producto.id])
            return format_html('<a href="{}">{}</a>', url, obj.producto.nombre)
        return "Producto eliminado"

    producto_link.short_description = "Producto"


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cliente",
        "fecha_creacion",
        "total",
        "estado",
        "codigo_seguimiento",
    )
    list_filter = ("estado", "fecha_creacion")
    search_fields = ("cliente__username", "id")
    list_editable = ["estado"]
    readonly_fields = (
        "id",
        "cliente",
        "fecha_creacion",
        "total",
        "direccion_envio",
        "ciudad_envio",
        "codigo_postal_envio",
        "telefono_contacto",
    )

    fieldsets = (
        (
            "Información del Pedido",
            {"fields": ("id", "cliente", "fecha_creacion", "total")},
        ),
        (
            "Estado y Seguimiento (Tu Gestión)",
            {"fields": ("estado", "metodo_envio_elegido", "codigo_seguimiento")},
        ),
        (
            "Datos de Envío (Cliente)",
            {
                "fields": (
                    "direccion_envio",
                    "ciudad_envio",
                    "codigo_postal_envio",
                    "telefono_contacto",
                )
            },
        ),
    )

    inlines = [ItemPedidoInline]

    actions = ["marcar_pagado_y_descontar_stock", "cancelar_pedidos_pendientes"]

    # 1. ACCIÓN NUEVA: Para confirmar el pago y descontar stock
    @admin.action(description="Marcar Pagado y Descontar Stock (Transferencias)")
    def marcar_pagado_y_descontar_stock(self, request, queryset):
        pedidos_confirmados = 0
        errores = []

        # Filtramos solo los que están esperando transferencia
        pedidos_a_procesar = queryset.filter(estado="pendiente_transferencia")

        for pedido in pedidos_a_procesar:
            success, error_msg = descontar_stock(pedido)

            if success:
                pedido.estado = "pagado"
                pedido.save()
                pedidos_confirmados += 1
            else:
                errores.append(f"Pedido #{pedido.id}: {error_msg}")

        if pedidos_confirmados > 0:
            self.message_user(
                request,
                f"{pedidos_confirmados} pedidos han sido confirmados y el stock ha sido descontado.",
                messages.SUCCESS,
            )
        if errores:
            self.message_user(
                request,
                f'Errores al descontar stock: {". ".join(errores)}',
                messages.ERROR,
            )

    # 2. ACCIÓN MODIFICADA: Para cancelar (ya no repone stock)
    @admin.action(description="Cancelar pedidos pendientes de transferencia")
    def cancelar_pedidos_pendientes(self, request, queryset):
        pedidos_actualizados = queryset.filter(estado="pendiente_transferencia").update(
            estado="cancelado"
        )

        if pedidos_actualizados > 0:
            self.message_user(
                request,
                f"{pedidos_actualizados} pedidos han sido cancelados.",
                messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                'Esta acción solo aplica a pedidos en estado "pendiente_transferencia".',
                messages.WARNING,
            )

    # --- FIN DE CAMBIOS EN ACCIONES ---

    def save_model(self, request, obj, form, change):
        # Lógica para enviar email cuando se añade código de seguimiento
        old_codigo_seguimiento = ""
        if change:
            try:
                old_codigo_seguimiento = (
                    Pedido.objects.get(pk=obj.pk).codigo_seguimiento or ""
                )
            except Pedido.DoesNotExist:
                pass

        super().save_model(request, obj, form, change)

        new_codigo_seguimiento = obj.codigo_seguimiento or ""

        if (
            new_codigo_seguimiento != old_codigo_seguimiento
            and new_codigo_seguimiento != ""
        ):
            # --- NUEVA LÓGICA DE EMAIL DINÁMICO ---
            # Aquí llamamos a tu función que busca el texto en el Admin
            enviar_email_dinamico(
                "DESPACHADO", 
                obj, 
                codigo_seguimiento=new_codigo_seguimiento
            )

            # Actualizamos el estado si no estaba ya despachado
            if obj.estado != "despachado":
                obj.estado = "despachado"
                obj.save()

            self.message_user(
                request, "Código guardado y email dinámico enviado al cliente."
            )