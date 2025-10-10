from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import calendar
from datetime import datetime, timedelta
from .models import ReglaDisponibilidad, TurnoReservado
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import mercadopago
from django.conf import settings
from django.urls import reverse
from configuracion.models import DatosPago


# --- Vistas del Calendario (sin cambios) ---
def calendario_view(request):
    today = datetime.now()
    year, month = today.year, today.month
    cal = calendar.Calendar()
    month_calendar = cal.monthdatescalendar(year, month)
    reglas = ReglaDisponibilidad.objects.filter(activa=True)
    dias_disponibles = set()
    for dia in cal.itermonthdates(year, month):
        if dia >= today.date() and reglas.filter(dia_semana=dia.weekday()).exists():
            dias_disponibles.add(dia)
    context = {
        'year': year, 'month_name': calendar.month_name[month],
        'month_calendar': month_calendar, 'current_month': month,
        'today': today.date(), 'dias_disponibles': dias_disponibles,
    }
    return render(request, 'turnos/calendario.html', context)

def horarios_disponibles_api(request, date_str):
    fecha = datetime.strptime(date_str, '%Y-%m-%d').date()
    horarios_finales = []
    try:
        regla = ReglaDisponibilidad.objects.get(dia_semana=fecha.weekday(), activa=True)
        horas_reservadas = {t.hora for t in TurnoReservado.objects.filter(fecha=fecha)}
        hora_actual = datetime.combine(fecha, regla.hora_inicio)
        hora_fin = datetime.combine(fecha, regla.hora_fin)
        while hora_actual < hora_fin:
            if hora_actual.time() not in horas_reservadas:
                if (fecha == datetime.now().date() and hora_actual.time() > datetime.now().time()) or fecha > datetime.now().date():
                    horarios_finales.append(hora_actual.strftime('%H:%M'))
            hora_actual += timedelta(hours=1)
    except ReglaDisponibilidad.DoesNotExist:
        pass
    return JsonResponse({'horarios': horarios_finales})


# --- VISTA DE CHECKOUT CON CORRECCIÓN FINAL ---
@login_required
def checkout_turno_view(request):
    fecha_str = request.GET.get('fecha')
    hora_str = request.GET.get('hora')
    
    if not fecha_str or not hora_str:
        messages.error(request, "Falta la fecha o la hora del turno.")
        return redirect('calendario')

    turno, created = TurnoReservado.objects.get_or_create(
        cliente=request.user, fecha=fecha_str, hora=hora_str,
        defaults={'estado': 'pendiente'}
    )
    request.session['turno_id_pendiente'] = turno.id

    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    preference_data = {
        "items": [{
            "title": f"Consulta Nutricional - {fecha_str} a las {hora_str}",
            "quantity": 1, "unit_price": float(settings.PRECIO_CONSULTA), "currency_id": "ARS"
        }],
        "payer": {
            "email": request.user.email,
        },
        "back_urls": {
            "success": request.build_absolute_uri(reverse('pago_exitoso')),
            "failure": request.build_absolute_uri(reverse('pago_fallido')),
            "pending": request.build_absolute_uri(reverse('pago_pendiente')),
        },
        # "auto_return": "approved", # <-- ELIMINAMOS ESTA LÍNEA QUE CAUSABA EL CONFLICTO
        "external_reference": turno.id,
    }
    
    preference_response = sdk.preference().create(preference_data)

    if preference_response.get("status") != 201:
        print("Error en la respuesta de Mercado Pago:", preference_response)
        messages.error(request, "Hubo un error al comunicarse con Mercado Pago. Revisa la consola del servidor.")
        return redirect('calendario')

    preference = preference_response["response"]
    preference_id = preference.get('id')
    
    if not preference_id:
        messages.error(request, "No se pudo obtener un ID de pago. Revisa la configuración de Mercado Pago.")
        return redirect('calendario')

    contexto = {
        'public_key': settings.MERCADO_PAGO_PUBLIC_KEY, 'preference_id': preference_id,
        'precio': settings.PRECIO_CONSULTA, 'datos_pago': DatosPago.objects.first(), 'turno': turno,
    }
    return render(request, 'turnos/checkout_turno.html', contexto)


# ... (el resto de tus vistas se quedan igual) ...

@login_required
def confirmar_reserva_view(request):
    turno_id = request.session.get('turno_id_pendiente')
    if not turno_id:
        messages.error(request, "No se encontró un turno pendiente.")
        return redirect('calendario')
    turno = get_object_or_404(TurnoReservado, id=turno_id)
    # Aquí puedes añadir la lógica para enviar el email de confirmación de transferencia
    return render(request, 'turnos/confirmacion_turno.html', {'turno': turno})


def pago_exitoso_view(request):
    turno_id = request.GET.get('external_reference')
    turno = get_object_or_404(TurnoReservado, id=turno_id)
    if request.GET.get('status') == 'approved':
        turno.estado = 'confirmado'
        turno.save()
    return render(request, 'turnos/pago_exitoso.html', {'turno': turno})

def pago_pendiente_view(request):
    turno_id = request.GET.get('external_reference')
    turno = get_object_or_404(TurnoReservado, id=turno_id)
    return render(request, 'turnos/pago_pendiente.html', {'turno': turno})

def pago_fallido_view(request):
    turno_id = request.GET.get('external_reference')
    turno = get_object_or_404(TurnoReservado, id=turno_id)
    turno.estado = 'cancelado'
    turno.save()
    return render(request, 'turnos/pago_fallido.html', {'turno': turno})

