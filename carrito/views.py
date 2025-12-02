from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.db import transaction 

import json
from decimal import Decimal
import mercadopago

from django.core.mail import send_mail
from django.template.loader import render_to_string
from pynliner import Pynliner 

from .models import Pedido, ItemPedido
from productos.models import Producto
from usuarios.models import Perfil
from turnos.models import TurnoReservado
from configuracion.models import DatosPago, AparienciaConfig

# ===================================================
# FUNCIONES AUXILIARES DE STOCK
# ===================================================

def descontar_stock(pedido):
    """
    Descuenta el stock de los productos de un pedido de forma segura.
    """
    try:
        with transaction.atomic():
            for item in pedido.items.all():
                producto = item.producto
                if producto.stock >= item.cantidad:
                    producto.stock -= item.cantidad
                    producto.save()
                else:
                    raise Exception(f"Stock insuficiente para {producto.nombre} al descontar.")
            return True, ""
    except Exception as e:
        print(f"Error grave al descontar stock para Pedido {pedido.id}: {e}")
        return False, str(e)

def reponer_stock(pedido):
    """
    Devuelve el stock de un pedido cancelado.
    """
    try:
        with transaction.atomic():
            for item in pedido.items.all():
                producto = item.producto
                producto.stock += item.cantidad
                producto.save()
            return True
    except Exception as e:
        print(f"Error grave al reponer stock para Pedido {pedido.id}: {e}")
        return False

# ===================================================
# VISTAS DE PEDIDOS (API Y CHECKOUT)
# ===================================================

@csrf_protect 
@login_required
def crear_pedido_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            carrito_items = data.get('cart')
            shipping_data = data.get('shipping')

            if not carrito_items:
                return JsonResponse({'error': 'El carrito está vacío'}, status=400)

            perfil = request.user.perfil
            if not perfil.direccion or not perfil.ciudad or not perfil.codigo_postal or not perfil.telefono:
                return JsonResponse({
                    'error': 'Por favor, completa tus datos de envío en "Mi Cuenta" antes de continuar.',
                    'redirect_url': reverse('edit_profile')
                }, status=400)

            subtotal_pedido = Decimal('0.00')
            items_para_crear = []

            # Validación de stock inicial (para evitar race conditions)
            with transaction.atomic():
                ids_productos = [item_data['id'] for item_data in carrito_items]
                productos_en_db = Producto.objects.select_for_update().filter(id__in=ids_productos)
                productos_map = {str(p.id): p for p in productos_en_db}

                for item_data in carrito_items:
                    producto = productos_map.get(item_data['id'])
                    
                    if not producto:
                        raise Producto.DoesNotExist(f"Producto ID {item_data['id']} no encontrado.")

                    cantidad_pedida = item_data['quantity']
                    
                    if producto.stock >= cantidad_pedida:
                        costo_item = producto.precio * cantidad_pedida
                        subtotal_pedido += costo_item
                        items_para_crear.append({
                            'producto': producto,
                            'cantidad': cantidad_pedida,
                            'precio_unitario': producto.precio
                        })
                    else:
                        return JsonResponse({
                            'error': f'Lo sentimos, solo quedan {producto.stock} unidades de {producto.nombre}.'
                        }, status=400)

                costo_envio = Decimal('0.00')
                metodo_envio_nombre = "Retiro"

                if shipping_data and shipping_data.get('precio'):
                    costo_envio = Decimal(str(shipping_data['precio']))
                    metodo_envio_nombre = shipping_data.get('nombre', 'Envío seleccionado')

                total_pedido = subtotal_pedido + costo_envio

                pedido = Pedido.objects.create(
                    cliente=request.user,
                    direccion_envio=perfil.direccion,
                    ciudad_envio=perfil.ciudad,
                    codigo_postal_envio=perfil.codigo_postal,
                    telefono_contacto=perfil.telefono,
                    total=total_pedido,
                    costo_envio=costo_envio,
                    metodo_envio_elegido=metodo_envio_nombre,
                    estado='pendiente' 
                )

                for item in items_para_crear:
                    ItemPedido.objects.create(
                        pedido=pedido,
                        producto=item['producto'],
                        cantidad=item['cantidad'],
                        precio_unitario=item['precio_unitario']
                    )

            checkout_url = reverse('checkout_pedido', args=[pedido.id])
            return JsonResponse({'success': True, 'redirect_url': checkout_url})

        except Producto.DoesNotExist as e:
            return JsonResponse({'error': f'Un producto en tu carrito ya no existe. {e}'}, status=400)
        except Exception as e:
            print(f"Error inesperado creando pedido: {e}")
            return JsonResponse({'error': 'Ocurrió un error inesperado al procesar tu pedido.'}, status=500)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)


@login_required
def checkout_pedido_view(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)

    if pedido.estado == 'pagado':
        messages.info(request, "Este pedido ya ha sido pagado.")
        return redirect('inicio')
    
    # Si el usuario vuelve de una transferencia pendiente para pagar con tarjeta
    if pedido.estado == 'pendiente_transferencia':
        pedido.estado = 'pendiente'
        pedido.save()

    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
    items_mp = [
        {
            "title": item.producto.nombre,
            "quantity": item.cantidad,
            "unit_price": float(item.precio_unitario),
            "currency_id": "ARS",
        }
        for item in pedido.items.all()
    ]

    if pedido.costo_envio > 0:
        items_mp.append({
            "title": f"Envío ({pedido.metodo_envio_elegido})",
            "quantity": 1,
            "unit_price": float(pedido.costo_envio),
            "currency_id": "ARS",
        })

    back_urls = {
        "success": request.build_absolute_uri(reverse('pago_exitoso_pedido')),
        "failure": request.build_absolute_uri(reverse('pago_fallido_pedido')),
        "pending": request.build_absolute_uri(reverse('pago_pendiente_pedido')),
    }

    preference_data = {
        "items": items_mp,
        "payer": {"email": request.user.email},
        "back_urls": back_urls,
        "external_reference": f"pedido-{pedido.id}",
    }

    try:
        preference_response = sdk.preference().create(preference_data)
        
        if preference_response.get("status") != 201:
            print("Error al crear preferencia MP:", preference_response)
            messages.error(request, "Hubo un error al conectar con Mercado Pago. Intenta más tarde.")
            return redirect('inicio')

        preference = preference_response["response"]
        preference_id = preference.get("id")

        if not preference_id:
            raise Exception("Preferencia ID no recibido")

    except Exception as e:
        print(f"Error MercadoPago: {e}")
        messages.error(request, "Error iniciando el pago. Intente nuevamente.")
        return redirect('inicio')

    contexto = {
        'pedido': pedido,
        'public_key': settings.MERCADO_PAGO_PUBLIC_KEY,
        'preference_id': preference_id,
        'datos_pago': DatosPago.objects.first(),
    }
    return render(request, 'carrito/checkout_pedido.html', contexto)


@login_required
def confirmar_transferencia_view(request, pedido_id):
    """
    Procesa la reserva del pedido por transferencia.
    NO descuenta stock (esto se hace al confirmar el pago en el admin).
    """
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)

    if pedido.estado == 'pendiente':
        # Doble validación de stock antes de reservar
        for item in pedido.items.all():
            if item.producto.stock < item.cantidad:
                messages.error(request, f"Lo sentimos, no queda stock suficiente para {item.producto.nombre}")
                return redirect('checkout_pedido', pedido_id=pedido.id)
        
        # Reservamos el pedido
        pedido.estado = 'pendiente_transferencia'
        pedido.save()
            
        # Enviamos email con instrucciones
        try:
            apariencia_config = AparienciaConfig.objects.first()
            datos_pago = DatosPago.objects.first()
            
            subject = f"Instrucciones de pago para tu Pedido #{pedido.id}"
            context = {
                'pedido': pedido, 
                'cliente': request.user,
                'datos_pago': datos_pago,
                'apariencia_config': apariencia_config
            }

            message_txt = render_to_string('carrito/email/instrucciones_transferencia.txt', context)
            message_html = render_to_string('carrito/email/instrucciones_transferencia.html', context)
            
            p = Pynliner()
            message_html_inlined = p.from_string(message_html).run()

            send_mail(
                subject, 
                message_txt, 
                settings.DEFAULT_FROM_EMAIL, 
                [request.user.email],
                html_message=message_html_inlined 
            )
        except Exception as e:
            print(f"Error al enviar email de transferencia para Pedido {pedido.id}: {e}")

        # Redirigimos a la nueva página de confirmación
        return redirect('pedido_confirmado_transferencia', pedido_id=pedido.id)
            
    elif pedido.estado == 'pendiente_transferencia':
        return redirect('pedido_confirmado_transferencia', pedido_id=pedido.id)
    else:
        messages.error(request, "Este pedido no se puede pagar por transferencia.")
        return redirect('inicio')


@login_required
def pedido_confirmado_transferencia_view(request, pedido_id):
    """
    Muestra la pantalla de éxito específica para transferencias.
    """
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    datos_pago = DatosPago.objects.first()
    
    contexto = {
        'pedido': pedido,
        'datos_pago': datos_pago
    }
    return render(request, 'carrito/pedido_confirmado_transferencia.html', contexto)


# ---------------------------------------------------
# ✅ VISTAS DE FEEDBACK DE PAGO
# ---------------------------------------------------
def pago_exitoso_pedido_view(request):
    external_ref = request.GET.get('external_reference')
    if external_ref:
        pedido_id = external_ref.split('-')[1]
        pedido = get_object_or_404(Pedido, id=pedido_id)
        return render(request, 'carrito/pago_exitoso_pedido.html', {'pedido': pedido})
    return redirect('inicio')


def pago_pendiente_pedido_view(request):
    # Esta vista se usa para pagos pendientes de Mercado Pago
    external_ref = request.GET.get('external_reference')
    pedido_id = None
    
    if external_ref:
        pedido_id = external_ref.split('-')[1]
    
    if not pedido_id:
        return redirect('inicio')

    pedido = get_object_or_404(Pedido, id=pedido_id)
    return render(request, 'carrito/pago_pendiente_pedido.html', {'pedido': pedido})


def pago_fallido_pedido_view(request):
    external_ref = request.GET.get('external_reference')
    if external_ref:
        pedido_id = external_ref.split('-')[1]
        pedido = get_object_or_404(Pedido, id=pedido_id)
        return render(request, 'carrito/pago_fallido_pedido.html', {'pedido': pedido})
    return redirect('inicio')


# ---------------------------------------------------
# ✅ WEBHOOK DE MERCADO PAGO
# ---------------------------------------------------
@csrf_exempt
def mercadopago_webhook_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponse(status=400)

        if data.get("type") == "payment":
            payment_id = data.get("data", {}).get("id")

            if not payment_id:
                return HttpResponse(status=400)

            try:
                sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
                payment_info = sdk.payment().get(payment_id)

                if payment_info.get("status") == 200:
                    payment = payment_info["response"]
                    external_ref = payment.get("external_reference")
                    payment_status = payment.get("status")

                    if not external_ref:
                        return HttpResponse(status=200) 

                    # CASO 1: Pedido de Productos
                    if external_ref.startswith("pedido-"):
                        pedido_id = external_ref.split('-')[1]
                        pedido = Pedido.objects.get(id=pedido_id)

                        if payment_status == "approved" and pedido.estado != 'pagado':
                            pedido.estado = 'pagado'
                            pedido.save()
                            success, error_msg = descontar_stock(pedido)
                            if not success:
                                print(f"¡ALERTA! Pedido {pedido.id} PAGADO pero NO SE DESCONTÓ STOCK. Error: {error_msg}")
                        
                        elif payment_status == "rejected" or payment_status == "cancelled":
                            pedido.estado = 'cancelado' 
                            pedido.save()

                    # CASO 2: Reserva de Turnos
                    elif external_ref.startswith("turno-"):
                        turno_id = external_ref.split('-')[1]
                        turno = TurnoReservado.objects.get(id=turno_id)
                        if payment_status == "approved" and turno.estado != 'confirmado':
                            turno.estado = 'confirmado'
                            turno.save()
                        elif payment_status == "rejected" or payment_status == "cancelled":
                            turno.estado = 'cancelado'
                            turno.save()

                    # CASO 3: Compra de Recetario
                    elif external_ref.startswith("recetario-"):
                        user_id = external_ref.split('-')[1]
                        try:
                            perfil = Perfil.objects.get(user_id=user_id)
                            perfil.es_cliente_activo = True
                            perfil.save()
                            print(f"Acceso al recetario CONCEDIDO al usuario ID {user_id}")
                        except Perfil.DoesNotExist:
                            print(f"¡ALERTA! Se pagó por el recetario (user_id: {user_id}) pero el perfil no existe.")
                    
            except Exception as e:
                print(f"Error procesando webhook: {e}")
                return HttpResponse(status=500)

    return HttpResponse(status=200)