from django.shortcuts import render, redirect, get_object_or_404
from productos.models import Producto
from recetas.models import Receta
from paginas.models import Pagina
from configuracion.models import HeroSectionConfig, CarruselImagen 
from configuracion.models import Servicio
from django.contrib.auth.decorators import login_required # <-- AÑADE ESTA LÍNEA
from django.contrib import messages
from django.conf import settings # <-- AÑADE ESTA LÍNEA
from django.urls import reverse # <-- AÑADE ESTA LÍNEA
import mercadopago

def inicio(request):
   
    productos_destacados = Producto.objects.filter(disponible=True, destacado=True)[:3]
    receta_aleatoria = Receta.objects.exclude(imagen__exact='').order_by('?').first()
    hero_config = HeroSectionConfig.objects.filter(activa=True).first()

    
    imagenes_carrusel = CarruselImagen.objects.filter(activo=True).order_by('orden')

    contexto = {
        'productos': productos_destacados,
        'receta': receta_aleatoria,
        'hero_config': hero_config,
        'imagenes_carrusel': imagenes_carrusel, 
    }
    return render(request, "inicio.html", contexto)


def sobre_mi_view(request):
    pagina = get_object_or_404(Pagina, slug='sobre-mi')
    contexto = {
        'pagina': pagina
    }
    return render(request, 'sobre_mi.html', contexto)

def servicios_view(request):
    """
    Muestra la página de planes y servicios que están activos
    y se pueden contratar.
    """
    # 2. Obtiene solo los servicios "activos" y los ordena
    servicios = Servicio.objects.filter(activo=True).order_by('orden')
    
    contexto = {
        'servicios': servicios
    }
    
    # 3. Renderiza la nueva plantilla que vamos a crear
    return render(request, 'core/servicios.html', contexto)



@login_required # El usuario debe estar logueado para comprar
def checkout_recetario_view(request):
    """
    Crea la preferencia de pago de Mercado Pago para el servicio de Recetario.
    """
    
    # 1. Verificar si el usuario YA tiene acceso
    if request.user.perfil.es_cliente_activo:
        messages.info(request, "¡Ya tienes acceso completo al recetario!")
        return redirect('recetario') # Lo mandamos a la página de recetas

    # 2. Obtener el servicio y su precio desde el modelo
    try:
        servicio_recetario = Servicio.objects.get(tipo_servicio='RECETARIO', activo=True)
    except Servicio.DoesNotExist:
        messages.error(request, "El servicio de recetario no está disponible en este momento.")
        return redirect('servicios')
    except Servicio.MultipleObjectsReturned:
        # Si tienes varios "Recetarios", toma el primero.
        servicio_recetario = Servicio.objects.filter(tipo_servicio='RECETARIO', activo=True).first()

    # 3. Configurar Mercado Pago
    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    # 4. Definir las URLs de retorno (éxito, fallo, pendiente)
    back_urls = {
        "success": request.build_absolute_uri(reverse('recetario')), # Si paga bien, va directo al recetario
        "failure": request.build_absolute_uri(reverse('servicios')), # Si falla, vuelve a servicios
        "pending": request.build_absolute_uri(reverse('servicios')), # Si queda pendiente, vuelve a servicios
    }

    # 5. Crear la preferencia de pago
    preference_data = {
        "items": [
            {
                "title": servicio_recetario.nombre,
                "quantity": 1,
                "unit_price": float(servicio_recetario.precio),
                "currency_id": "ARS",
            }
        ],
        "payer": {"email": request.user.email},
        "back_urls": back_urls,
        # ¡ESTO ES CLAVE! El webhook usará esto para saber QUÉ se pagó y QUIÉN lo pagó.
        "external_reference": f"recetario-{request.user.id}",
    }

    try:
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]
        preference_id = preference.get("id")
        
        if not preference_id:
            raise Exception("No se pudo obtener la preferencia de pago.")

    except Exception as e:
        print(f"Error al crear preferencia MP para Recetario: {e}")
        messages.error(request, "Hubo un error al conectar con Mercado Pago. Intenta más tarde.")
        return redirect('servicios')

    # 6. Renderizar la página de checkout con el botón de pago
    contexto = {
        'servicio': servicio_recetario,
        'public_key': settings.MERCADO_PAGO_PUBLIC_KEY,
        'preference_id': preference_id
    }

    return render(request, 'core/checkout_recetario.html', contexto)