from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse

import json
import mercadopago

# Modelos
from productos.models import Producto
from recetas.models import Receta
from paginas.models import Pagina
from configuracion.models import HeroSectionConfig, CarruselImagen, Servicio, ConfigPrecio

# ========================================================
# 1. PÁGINA DE INICIO
# ========================================================
def inicio(request):
    """Vista principal (Home)."""
    productos_destacados = Producto.objects.filter(disponible=True, destacado=True)[:3]
    receta_aleatoria = Receta.objects.exclude(imagen__exact='').order_by('?').first()
    hero_config = HeroSectionConfig.objects.filter(activa=True).first()
    imagenes_carrusel = CarruselImagen.objects.filter(activo=True).order_by('orden')

    # Usamos 'context' consistentemente
    context = {
        'productos': productos_destacados,
        'receta': receta_aleatoria,
        'hero_config': hero_config,
        'imagenes_carrusel': imagenes_carrusel, 
    }
    return render(request, "inicio.html", context)


# ========================================================
# 2. PÁGINA SOBRE MÍ
# ========================================================
def sobre_mi_view(request):
    try:
        pagina = Pagina.objects.get(slug='sobre-mi')
    except Pagina.DoesNotExist:
        pagina = None
    return render(request, 'sobre_mi.html', {'pagina': pagina})


# ========================================================
# 3. LISTADO DE SERVICIOS
# ========================================================
def servicios_view(request):
    """Muestra planes y servicios con precios globales."""
    servicios = Servicio.objects.filter(activo=True).order_by('orden')
    
    # Precios globales para visualización
    config_precios = ConfigPrecio.objects.first()
    precio_consulta_global = config_precios.precio_consulta if config_precios else 1500.00
    precio_recetario_global = config_precios.precio_recetario_mensual if config_precios else 3000.00
    
    # Usamos 'context' consistentemente
    context = {
        'servicios': servicios,
        'precio_consulta_global': precio_consulta_global,
        'precio_recetario_global': precio_recetario_global
    }
    return render(request, 'core/servicios.html', context)


# ========================================================
# 4. CHECKOUT DE RECETARIO (Suscripción)
# ========================================================
@login_required 
def checkout_recetario_view(request):
    """
    Crea la preferencia de pago de Mercado Pago para el acceso al Recetario.
    """
    
    # 1. Verificar si ya tiene acceso
    if request.user.perfil.es_cliente_activo:
        messages.info(request, "¡Ya tienes acceso completo al recetario!")
        return redirect('recetario') 

    # 2. Obtener servicio base
    servicio_recetario = Servicio.objects.filter(tipo_servicio='RECETARIO', activo=True).first()
    
    if not servicio_recetario:
        messages.error(request, "El servicio de recetario no está disponible.")
        return redirect('servicios')

    # 3. Determinar Precio (Global vs Individual)
    config_precios = ConfigPrecio.objects.first()
    if config_precios:
        precio_final = float(config_precios.precio_recetario_mensual)
    else:
        precio_final = float(servicio_recetario.precio)

    # 4. Configurar Mercado Pago
    token = settings.MERCADO_PAGO_ACCESS_TOKEN
    sdk = mercadopago.SDK(token)
    
    host = request.build_absolute_uri('/')[:-1] 
    
    # Construimos URLs absolutas seguras
    back_urls = {
        "success": f"{host}{reverse('recetario')}", 
        "failure": f"{host}{reverse('servicios')}", 
        "pending": f"{host}{reverse('servicios')}", 
    }

    preference_data = {
        "items": [
            {
                "title": servicio_recetario.nombre,
                "quantity": 1,
                "unit_price": precio_final,
                "currency_id": "ARS",
            }
        ],
        "payer": {"email": request.user.email},
        "back_urls": back_urls,
        
        # --- CORRECCIÓN ---
        # Comentamos auto_return para evitar error 400 en localhost
        # "auto_return": "approved",
        # ------------------
        
        "external_reference": f"recetario-{request.user.id}",
    }

    try:
        print(f"📦 RECETARIO: Enviando pref a MP con precio ${precio_final}...")
        preference_response = sdk.preference().create(preference_data)
        
        if preference_response.get("status") not in [200, 201]:
            print(f"❌ ERROR MP: {preference_response.get('response')}")
            raise Exception("MP rechazó la creación.")
            
        preference = preference_response["response"]
        preference_id = preference.get("id")
        
        if not preference_id:
            raise Exception("ID de preferencia no recibido.")
            
        print(f"✅ ID Creado: {preference_id}")

    except Exception as e:
        print(f"❌ EXCEPCIÓN CRÍTICA: {e}")
        messages.error(request, "Error de conexión con Mercado Pago.")
        return redirect('servicios')

    # 6. Renderizar checkout
    context = {
        'servicio': servicio_recetario,
        'precio': precio_final,
        'public_key': settings.MERCADO_PAGO_PUBLIC_KEY,
        'preference_id': preference_id
    }

    return render(request, 'core/checkout_recetario.html', context)