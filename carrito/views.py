# carrito/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse

import json
from decimal import Decimal
import mercadopago

from .models import Pedido, ItemPedido
from productos.models import Producto
from usuarios.models import Perfil
from turnos.models import TurnoReservado
from configuracion.models import DatosPago


# ---------------------------------------------------
# ✅ CREAR PEDIDO (API)
# ---------------------------------------------------
@csrf_exempt
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

            # --- Cálculo de montos ---
            subtotal_pedido = Decimal('0.00')
            items_para_crear = []

            for item_data in carrito_items:
                producto = Producto.objects.get(id=item_data['id'])

                if producto.stock >= item_data['quantity']:
                    costo_item = producto.precio * item_data['quantity']
                    subtotal_pedido += costo_item
                    items_para_crear.append({
                        'producto': producto,
                        'cantidad': item_data['quantity'],
                        'precio_unitario': producto.precio
                    })
                else:
                    return JsonResponse({
                        'error': f'Lo sentimos, solo quedan {producto.stock} unidades de {producto.nombre}.'
                    }, status=400)

            # --- Costo de envío ---
            costo_envio = Decimal('0.00')
            metodo_envio_nombre = "Retiro"

            if shipping_data and shipping_data.get('precio'):
                costo_envio = Decimal(str(shipping_data['precio']))
                metodo_envio_nombre = shipping_data.get('nombre', 'Envío seleccionado')

            total_pedido = subtotal_pedido + costo_envio

            # --- Crear el pedido ---
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

            # --- Crear los items del pedido ---
            for item in items_para_crear:
                ItemPedido.objects.create(
                    pedido=pedido,
                    producto=item['producto'],
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio_unitario']
                )

            checkout_url = reverse('checkout_pedido', args=[pedido.id])
            return JsonResponse({'success': True, 'redirect_url': checkout_url})

        except Producto.DoesNotExist:
            return JsonResponse({'error': 'Un producto en tu carrito ya no existe.'}, status=400)
        except Exception as e:
            print(f"Error inesperado creando pedido: {e}")
            return JsonResponse({'error': 'Ocurrió un error inesperado al procesar tu pedido.'}, status=500)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)


# ---------------------------------------------------
# ✅ CHECKOUT PEDIDO (Mercado Pago)
# ---------------------------------------------------
@login_required
def checkout_pedido_view(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)

    if pedido.estado == 'pagado':
        messages.info(request, "Este pedido ya ha sido pagado.")
        return redirect('inicio')

    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    # --- Items de Mercado Pago ---
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

    # --- URLs de retorno ---
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

    preference_response = sdk.preference().create(preference_data)

    if preference_response.get("status") != 201:
        print("Error al crear preferencia MP:", preference_response)
        messages.error(request, "Hubo un error al conectar con Mercado Pago. Intenta más tarde.")
        return redirect('inicio')

    preference = preference_response["response"]
    preference_id = preference.get("id")

    if not preference_id:
        messages.error(request, "No se pudo obtener la preferencia de pago.")
        return redirect('inicio')

    contexto = {
        'pedido': pedido,
        'public_key': settings.MERCADO_PAGO_PUBLIC_KEY,
        'preference_id': preference_id,
        'datos_pago': DatosPago.objects.first(),
    }

    return render(request, 'carrito/checkout_pedido.html', contexto)


# ---------------------------------------------------
# ✅ VISTAS DE FEEDBACK DE PAGO
# ---------------------------------------------------
def pago_exitoso_pedido_view(request):
    pedido_id = request.GET.get('external_reference').split('-')[1]
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.GET.get('status') == 'approved':
        pedido.estado = 'pagado'
        pedido.save()

    return render(request, 'carrito/pago_exitoso_pedido.html', {'pedido': pedido})


def pago_pendiente_pedido_view(request):
    pedido_id = request.GET.get('external_reference').split('-')[1]
    pedido = get_object_or_404(Pedido, id=pedido_id)
    return render(request, 'carrito/pago_pendiente_pedido.html', {'pedido': pedido})


def pago_fallido_pedido_view(request):
    pedido_id = request.GET.get('external_reference').split('-')[1]
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.estado = 'cancelado'
    pedido.save()
    return render(request, 'carrito/pago_fallido_pedido.html', {'pedido': pedido})


# ---------------------------------------------------
# ✅ WEBHOOK DE MERCADO PAGO
# ---------------------------------------------------
@csrf_exempt
def mercadopago_webhook_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)

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

                    if payment_status == "approved":
                        if external_ref.startswith("pedido-"):
                            pedido_id = external_ref.split('-')[1]
                            pedido = Pedido.objects.get(id=pedido_id)
                            pedido.estado = 'pagado'
                            pedido.save()

                        elif external_ref.startswith("turno-"):
                            turno_id = external_ref.split('-')[1]
                            turno = TurnoReservado.objects.get(id=turno_id)
                            turno.estado = 'confirmado'
                            turno.save()

            except Exception as e:
                print(f"Error procesando webhook: {e}")
                return HttpResponse(status=500)

    return HttpResponse(status=200)
