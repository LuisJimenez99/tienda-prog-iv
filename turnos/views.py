from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta

import json
import mercadopago

from django.core.mail import send_mail

from .models import ReglaDisponibilidad, TurnoReservado
from configuracion.models import DatosPago, Servicio, AparienciaConfig, ConfigPrecio  # <-- Importamos ConfigPrecio

# ========================================================
# 1. VISTA PRINCIPAL (Calendario)
# ========================================================
def calendario_view(request):
    """
    Renderiza la estructura HTML. 
    Flatpickr (JS) se encargará de pedir los datos a la API.
    """
    servicios = Servicio.objects.filter(tipo_servicio='TURNO', activo=True)
    
    # Obtenemos el precio actual para mostrarlo si hiciera falta
    config_precios = ConfigPrecio.objects.first()
    precio_actual = config_precios.precio_consulta if config_precios else 1500.00

    return render(request, 'turnos/calendario.html', {
        'servicios': servicios,
        'precio_consulta': precio_actual
    })


# ========================================================
# 2. API DE HORARIOS (Lógica corregida)
# ========================================================
def horarios_disponibles_api(request):
    """
    Recibe ?fecha=YYYY-MM-DD y devuelve los horarios libres.
    """
    date_str = request.GET.get('fecha')
    if not date_str:
        return JsonResponse({'error': 'Fecha requerida'}, status=400)
    
    try:
        fecha = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Formato inválido'}, status=400)

    if fecha < timezone.now().date():
        return JsonResponse({'horarios': []})

    # 1. Buscamos TODAS las reglas para ese día
    dia_semana_num = fecha.weekday()
    reglas = ReglaDisponibilidad.objects.filter(dia_semana=dia_semana_num, activa=True)

    # 2. Buscamos horas YA ocupadas
    horas_reservadas = set(
        TurnoReservado.objects.filter(
            fecha=fecha, 
            estado__in=['confirmado', 'pendiente', 'esperando_confirmacion']
        ).values_list('hora', flat=True)
    )

    horarios_posibles = set() 
    duracion_turno = timedelta(minutes=60) 

    # 3. Generamos slots
    for regla in reglas:
        hora_actual = datetime.combine(fecha, regla.hora_inicio)
        hora_fin = datetime.combine(fecha, regla.hora_fin)
        
        while hora_actual < hora_fin:
            hora_time = hora_actual.time()
            
            if hora_time not in horas_reservadas:
                es_hoy = fecha == timezone.now().date()
                hora_pasada = hora_time <= timezone.now().time()
                
                if not (es_hoy and hora_pasada):
                    horarios_posibles.add(hora_actual.strftime('%H:%M'))
            
            hora_actual += duracion_turno

    lista_final = sorted(list(horarios_posibles))
    return JsonResponse({'horarios': lista_final})


# ========================================================
# 3. RESERVAR (Crear Turno)
# ========================================================
@login_required
def reservar_turno(request):
    if request.method == 'POST':
        fecha_str = request.POST.get('fecha')
        hora_str = request.POST.get('hora')
        
        if not fecha_str or not hora_str:
            messages.error(request, "Faltan datos.")
            return redirect('calendario')

        turno, created = TurnoReservado.objects.get_or_create(
            cliente=request.user,
            fecha=fecha_str,
            hora=hora_str,
            defaults={'estado': 'pendiente'}
        )
        return redirect('checkout_turno', turno_id=turno.id)
    
    return redirect('calendario')


# ========================================================
# 4. CHECKOUT (Mercado Pago con Precio Dinámico)
# ========================================================
@login_required
def checkout_turno_view(request, turno_id):
    turno = get_object_or_404(TurnoReservado, id=turno_id, cliente=request.user)
    
    if turno.estado == 'confirmado':
        messages.info(request, "Este turno ya está confirmado.")
        return redirect('inicio')

    # 1. OBTENER PRECIO DINÁMICO (NUEVO)
    config_precios = ConfigPrecio.objects.first()
    # Si no existe configuración, usamos un valor por defecto seguro
    precio_actual = float(config_precios.precio_consulta) if config_precios else 1500.00

    # 2. Configurar SDK
    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
    host = request.build_absolute_uri('/')[:-1] 

    url_success = request.build_absolute_uri(reverse('pago_exitoso'))
    url_failure = request.build_absolute_uri(reverse('pago_fallido'))
    url_pending = request.build_absolute_uri(reverse('pago_pendiente'))

    # 3. Datos del Pagador
    payer_email = request.user.email if request.user.email else "test_user_123@test.com"

    preference_data = {
        "items": [{
            "title": f"Consulta Nutricional - {turno.fecha} {turno.hora}",
            "quantity": 1,
            "unit_price": precio_actual, # <-- USAMOS EL PRECIO DINÁMICO
            "currency_id": "ARS"
        }],
        "payer": { 
            "email": payer_email 
        },
        "back_urls": {
            "success": url_success,
            "failure": url_failure,
            "pending": url_pending,
        },
        # "auto_return": "approved", # Comentado para evitar error en localhost
        "external_reference": f"turno-{turno.id}",
    }
    
    try:
        preference_response = sdk.preference().create(preference_data)
        
        if preference_response.get("status") not in [200, 201]:
            print(f"ERROR MP: {preference_response.get('response')}")
            raise Exception("MP rechazó la creación.")

        preference = preference_response["response"]
        preference_id = preference.get('id')

    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")
        messages.error(request, "Error de conexión con Mercado Pago.")
        return redirect('calendario')

    contexto = {
        'public_key': settings.MERCADO_PAGO_PUBLIC_KEY, 
        'preference_id': preference_id,
        'precio': precio_actual, # Pasamos el precio correcto al template
        'datos_pago': DatosPago.objects.first(), 
        'turno': turno,
    }
    return render(request, 'turnos/checkout_turno.html', contexto)


# ========================================================
# 5. CONFIRMAR TRANSFERENCIA
# ========================================================
@login_required
def confirmar_transferencia_turno_view(request, turno_id):
    turno = get_object_or_404(TurnoReservado, id=turno_id, cliente=request.user)

    # Obtenemos precio para mostrar en el email/pantalla
    config_precios = ConfigPrecio.objects.first()
    precio_actual = config_precios.precio_consulta if config_precios else 1500.00

    if turno.estado == 'pendiente':
        try:
            apariencia_config = AparienciaConfig.objects.first()
            datos_pago = DatosPago.objects.first()
            
            subject = f"Reserva de Turno #{turno.id} - Pendiente de Transferencia"
            
            mensaje = f"""
            Hola {request.user.first_name},
            Has reservado un turno para el {turno.fecha} a las {turno.hora}.
            Transfiere ${precio_actual} al Alias: {datos_pago.cbu_alias}.
            """
            
            send_mail(subject, mensaje, settings.DEFAULT_FROM_EMAIL, [request.user.email])
        except Exception as e:
            print(f"Error enviando email turno: {e}")

    # Pasamos el precio al contexto también
    return render(request, 'turnos/pago_pendiente.html', {
        'turno': turno, 
        'precio': precio_actual,
        'datos_pago': DatosPago.objects.first()
    })


# ========================================================
# 6. RETORNOS DE PAGO
# ========================================================
@login_required
def pago_exitoso_view(request):
    external_ref = request.GET.get('external_reference')
    turno = None
    if external_ref and external_ref.startswith("turno-"):
        turno_id = external_ref.split('-')[1]
        turno = TurnoReservado.objects.filter(id=turno_id).first()
        if turno and turno.estado != 'confirmado':
            turno.estado = 'confirmado'
            turno.save()
    return render(request, 'turnos/pago_exitoso.html', {'turno': turno})

@login_required
def pago_pendiente_view(request):
    return render(request, 'turnos/pago_pendiente.html')

@login_required
def pago_fallido_view(request):
    return render(request, 'turnos/pago_fallido.html')