import csv
from django.http import HttpResponse
from django.contrib import admin, messages
from .models import Pedido, ItemPedido
from django.utils.html import format_html
from .emails import enviar_email_dinamico  # Importamos tu función de emails
from .views import descontar_stock  # Importamos la lógica de stock

# --- ACCIÓN PERSONALIZADA: EXPORTAR A EXCEL (CSV) ---
def exportar_a_csv(modeladmin, request, queryset):
    """
    Esta función toma los pedidos seleccionados y genera un archivo CSV
    que se puede abrir en Excel.
    """
    opts = modeladmin.model._meta
    content_disposition = f'attachment; filename={opts.verbose_name_plural}.csv'
    
    # Creamos la respuesta HTTP con tipo CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = content_disposition
    
    # Escribimos el BOM (Byte Order Mark) para que Excel reconozca los acentos (UTF-8)
    response.write(u'\ufeff'.encode('utf8'))
    
    writer = csv.writer(response)
    
    # 1. Encabezados de las columnas (La primera fila del Excel)
    fields = ['ID Pedido', 'Cliente', 'Fecha', 'Total ($)', 'Estado', 'Envío', 'Detalle de Productos']
    writer.writerow(fields)

    # 2. Llenamos las filas con los datos
    for obj in queryset:
        data_row = []
        
        # Datos básicos
        data_row.append(obj.id)
        data_row.append(obj.cliente.username if obj.cliente else "Invitado")
        data_row.append(obj.fecha_creacion.strftime("%d/%m/%Y %H:%M"))
        data_row.append(obj.total)
        data_row.append(obj.get_estado_display()) # Muestra el texto legible (ej: "Pagado")
        data_row.append(obj.metodo_envio_elegido)
        
        # Generamos un resumen de los items (ej: "2x Milanesa, 1x Tarta")
        # Esto es muy útil para la cocina
        items_str = " | ".join([f"{item.cantidad}x {item.producto.nombre}" for item in obj.items.all()])
        data_row.append(items_str)
        
        writer.writerow(data_row)
        
    return response

# Nombre que aparecerá en el menú "Acción" del Admin
exportar_a_csv.short_description = "Descargar Selección en Excel (CSV)"


# --- CONFIGURACIÓN DEL ADMIN (CLASES) ---

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

    # --- ACCIONES ---
    # Aquí registramos nuestras 3 herramientas poderosas
    actions = ["marcar_pagado_y_descontar_stock", "cancelar_pedidos_pendientes", exportar_a_csv]

    # Acción 1: Confirmar pago y stock
    @admin.action(description="Marcar Pagado y Descontar Stock (Transferencias)")
    def marcar_pagado_y_descontar_stock(self, request, queryset):
        pedidos_confirmados = 0
        errores = []
        
        # Solo procesamos los que están esperando transferencia
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

    # Acción 2: Cancelar sin tocar stock (porque nunca se descontó)
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

    # --- LÓGICA DE GUARDADO (EMAIL DINÁMICO) ---
    def save_model(self, request, obj, form, change):
        # Detectamos si cambió el código de seguimiento
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

        # Si hay un código nuevo, enviamos el email de despacho
        if (
            new_codigo_seguimiento != old_codigo_seguimiento
            and new_codigo_seguimiento != ""
        ):
            # Usamos la nueva función limpia que lee la configuración del Admin
            enviar_email_dinamico(
                "DESPACHADO", 
                obj, 
                codigo_seguimiento=new_codigo_seguimiento
            )

            # Actualizamos el estado automáticamente
            if obj.estado != "despachado":
                obj.estado = "despachado"
                obj.save()

            self.message_user(
                request, "Código guardado y email dinámico enviado al cliente."
            )