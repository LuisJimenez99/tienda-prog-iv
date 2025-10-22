from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from .models import Pedido, ItemPedido
from productos.models import Producto
from usuarios.models import Perfil  # Para obtener los datos de envío
import mercadopago
from django.conf import settings
from django.urls import reverse
from configuracion.models import DatosPago


@csrf_exempt  # Necesario para recibir datos POST desde JS sin recarga
@login_required
def crear_pedido_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            carrito_items = data.get('cart')

            if not carrito_items:
                return JsonResponse({'error': 'El carrito está vacío'}, status=400)

            # --- VERIFICACIÓN DE DATOS DE ENVÍO ---
            perfil = request.user.perfil
            if not perfil.direccion or not perfil.ciudad or not perfil.codigo_postal or not perfil.telefono:
                # Si faltan datos, devolvemos un error y la URL para editar el perfil
                return JsonResponse({
                    'error': 'Por favor, completa tus datos de envío en "Mi Cuenta" antes de continuar.',
                    'redirect_url': reverse('edit_profile')
                }, status=400)

            total_pedido = 0
            items_para_crear = []

            # Calculamos el total y preparamos los items, verificando stock
            for item_data in carrito_items:
                try:
                    producto = Producto.objects.get(id=item_data['id'])
                    # Verificamos si hay stock suficiente
                    if producto.stock >= item_data['quantity']:
                        costo_item = producto.precio * item_data['quantity']
                        total_pedido += costo_item
                        items_para_crear.append({
                            'producto': producto,
                            'cantidad': item_data['quantity'],
                            'precio_unitario': producto.precio
                        })
                    else:
                        # Si no hay stock, devolvemos un error específico
                        return JsonResponse({
                            'error': f'Lo sentimos, solo quedan {producto.stock} unidades de {producto.nombre}.'
                        }, status=400)
                except Producto.DoesNotExist:
                    return JsonResponse({
                        'error': f'Producto con ID {item_data["id"]} no encontrado.'
                    }, status=400)

            # Creamos el pedido en la base de datos
            pedido = Pedido.objects.create(
                cliente=request.user,
                direccion_envio=perfil.direccion,
                ciudad_envio=perfil.ciudad,
                codigo_postal_envio=perfil.codigo_postal,
                telefono_contacto=perfil.telefono,
                total=total_pedido,
                estado='pendiente'  # Empieza pendiente hasta que se pague
            )

            # Creamos los items asociados al pedido
            for item in items_para_crear:
                ItemPedido.objects.create(
                    pedido=pedido,
                    producto=item['producto'],
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio_unitario']
                )
                # Opcional: descontar stock aquí si lo deseas
                # producto = item['producto']
                # producto.stock -= item['cantidad']
                # producto.save()

            # Devolvemos la URL de la página de checkout del pedido recién creado
            checkout_url = reverse('checkout_pedido', args=[pedido.id])
            return JsonResponse({'success': True, 'redirect_url': checkout_url})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos del carrito inválidos.'}, status=400)
        except Exception as e:
            print(f"Error inesperado creando pedido: {e}")  # Loguea el error en consola
            return JsonResponse({'error': 'Ocurrió un error inesperado al procesar tu pedido.'}, status=500)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)


@login_required
def checkout_pedido_view(request, pedido_id):
    # Buscamos el pedido asegurándonos que pertenezca al usuario logueado
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)

    # Si el pedido ya está pagado, no mostramos las opciones de pago
    if pedido.estado == 'pagado':
        messages.info(request, "Este pedido ya ha sido pagado.")
        # Idealmente, redirigir a una página de 'detalle_pedido'
        return redirect('inicio')

    # Configuramos Mercado Pago
    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    items_mp = []
    for item in pedido.items.all():
        items_mp.append({
            "title": item.producto.nombre,
            "quantity": item.cantidad,
            "unit_price": float(item.precio_unitario),
            "currency_id": "ARS",
        })

    # Construimos las URLs de retorno completas
    back_urls = {
        "success": request.build_absolute_uri(reverse('pago_exitoso_pedido')),
        "failure": request.build_absolute_uri(reverse('pago_fallido_pedido')),
        "pending": request.build_absolute_uri(reverse('pago_pendiente_pedido')),
    }

    preference_data = {
        "items": items_mp,
        "payer": {"email": request.user.email},
        "back_urls": back_urls,
        "external_reference": pedido.id,  # Enviamos el ID de nuestro Pedido
    }

    preference_response = sdk.preference().create(preference_data)

    if preference_response.get("status") != 201:
        print("Error al crear preferencia MP:", preference_response)
        messages.error(request, "Hubo un error al conectar con Mercado Pago. Intenta más tarde.")
        return redirect('inicio')  # O redirigir al carrito

    preference = preference_response["response"]
    preference_id = preference.get("id")

    if not preference_id:
        messages.error(request, "No se pudo obtener la preferencia de pago.")
        return redirect('inicio')

    contexto = {
        'pedido': pedido,
        'public_key': settings.MERCADO_PAGO_PUBLIC_KEY,
        'preference_id': preference_id,
        'datos_pago': DatosPago.objects.first(),  # Para la opción de transferencia
    }

    return render(request, 'carrito/checkout_pedido.html', contexto)


# --- Vistas de Feedback de Pago para Pedidos ---

def pago_exitoso_pedido_view(request):
    pedido_id = request.GET.get('external_reference')
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.GET.get('status') == 'approved':
        pedido.estado = 'pagado'
        pedido.save()
        # Aquí enviarías email de confirmación de pedido pagado
    return render(request, 'carrito/pago_exitoso_pedido.html', {'pedido': pedido})


def pago_pendiente_pedido_view(request):
    pedido_id = request.GET.get('external_reference')
    pedido = get_object_or_404(Pedido, id=pedido_id)
    return render(request, 'carrito/pago_pendiente_pedido.html', {'pedido': pedido})


def pago_fallido_pedido_view(request):
    pedido_id = request.GET.get('external_reference')
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.estado = 'cancelado'
    pedido.save()
    return render(request, 'carrito/pago_fallido_pedido.html', {'pedido': pedido})
