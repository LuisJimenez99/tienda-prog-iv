import csv
import json
from datetime import datetime

from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.contrib.auth.models import User

# Modelos del Proyecto
from turnos.models import TurnoReservado, ReglaDisponibilidad
from carrito.models import Pedido
from usuarios.models import Perfil
from productos.models import Producto
from configuracion.models import ConfigPrecio
# Importamos los modelos de la historia clínica y expediente
from .models import Paciente, Consulta, ArchivoPaciente, PlanAlimentacion

# Formularios
from .forms import (
    ProductoForm, 
    ReglaDisponibilidadForm, 
    PacienteForm, 
    ConsultaForm, 
    ConfigPrecioForm,
    ArchivoPacienteForm,    # <-- Nuevo
    PlanAlimentacionForm    # <-- Nuevo
)


# ========================================================
# 1. INICIO (DASHBOARD RESUMEN)
# ========================================================
@staff_member_required(login_url='/accounts/login/')
def inicio_panel(request):
    """
    Dashboard principal: Resumen del día.
    """
    hoy = timezone.now().date()
    turnos_hoy = TurnoReservado.objects.filter(fecha=hoy, estado='confirmado').count()
    pedidos_pendientes = Pedido.objects.filter(estado='pagado').count()
    
    # KPIs de Suscripciones
    suscripciones_activas = Perfil.objects.filter(suscripcion_activa_hasta__gte=hoy).count()
    
    from datetime import timedelta
    limite_alerta = hoy + timedelta(days=5)
    suscripciones_venciendo = Perfil.objects.filter(
        suscripcion_activa_hasta__gte=hoy,
        suscripcion_activa_hasta__lte=limite_alerta
    ).count()
    
    context = {
        'turnos_hoy': turnos_hoy,
        'pedidos_cocina': pedidos_pendientes,
        'suscripciones_activas': suscripciones_activas,
        'suscripciones_venciendo': suscripciones_venciendo,
        'fecha_actual': hoy,
    }
    return render(request, 'panel_gestor/inicio.html', context)


# ========================================================
# 2. AGENDA PROFESIONAL
# ========================================================
@staff_member_required
def agenda_panel(request):
    """Muestra la estructura visual de la agenda."""
    return render(request, 'panel_gestor/agenda.html')

@staff_member_required
def api_turnos_dia(request):
    """
    API JSON: Recibe ?fecha=YYYY-MM-DD
    Devuelve la lista de pacientes y detalles para ese día.
    """
    date_str = request.GET.get('fecha')
    if not date_str:
        return JsonResponse({'turnos': []})

    try:
        fecha = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Fecha inválida'}, status=400)

    # Buscamos turnos de ese día (ordenados por hora)
    turnos = TurnoReservado.objects.filter(fecha=fecha).order_by('hora')
    
    data = []
    for t in turnos:
        nombre_paciente = t.cliente.username
        if t.cliente.first_name:
            nombre_paciente = f"{t.cliente.first_name} {t.cliente.last_name}"
            
        data.append({
            'id': t.id,
            'hora': t.hora.strftime('%H:%M'),
            'paciente': nombre_paciente,
            'email': t.cliente.email,
            'estado': t.get_estado_display(),
            'estado_code': t.estado 
        })
        
    return JsonResponse({'turnos': data})

@staff_member_required
@require_POST
def api_gestion_turno(request, turno_id):
    """
    Maneja acciones sobre un turno específico desde la Agenda.
    """
    turno = get_object_or_404(TurnoReservado, id=turno_id)
    
    try:
        data = json.loads(request.body)
        accion = data.get('accion')

        if accion == 'confirmar':
            turno.estado = 'confirmado'
            turno.save()
            mensaje = f"Turno confirmado."
            
        elif accion == 'cancelar':
            turno.estado = 'cancelado'
            turno.save()
            mensaje = f"Turno cancelado."
            
        elif accion == 'reagendar':
            nueva_fecha = data.get('fecha')
            nueva_hora = data.get('hora')
            modo = data.get('modo') # 'directo' o 'avisar'
            
            if not nueva_fecha or not nueva_hora:
                return JsonResponse({'success': False, 'error': 'Faltan datos'}, status=400)
            
            # Validación de disponibilidad
            ocupado = TurnoReservado.objects.filter(
                fecha=nueva_fecha, 
                hora=nueva_hora,
                estado__in=['confirmado', 'pendiente', 'esperando_confirmacion']
            ).exclude(id=turno.id).exists()
            
            if ocupado:
                return JsonResponse({
                    'success': False, 
                    'error': 'HORARIO_OCUPADO', 
                    'mensaje': 'El horario ya está ocupado.'
                }, status=409)

            turno.fecha = nueva_fecha
            turno.hora = nueva_hora
            
            if modo == 'avisar':
                turno.estado = 'esperando_confirmacion'
                mensaje = "Turno movido (Esperando Confirmación)."
            else:
                turno.estado = 'confirmado'
                mensaje = "Turno reagendado y confirmado."
            
            turno.save()
            
        else:
            return JsonResponse({'success': False, 'error': 'Acción desconocida'}, status=400)

        return JsonResponse({'success': True, 'mensaje': mensaje})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ========================================================
# 3. COCINA Y PEDIDOS (KANBAN)
# ========================================================
@staff_member_required
def cocina_panel(request):
    """
    Muestra los pedidos activos. Filtramos por estados operativos.
    """
    estado_filter = request.GET.get('estado')
    
    if estado_filter:
        pedidos = Pedido.objects.filter(estado=estado_filter).order_by('-fecha_creacion')
    else:
        pedidos = Pedido.objects.filter(
            estado__in=['pagado', 'en_preparacion', 'despachado']
        ).order_by('-fecha_creacion')

    context = {
        'pedidos': pedidos,
        'estado_actual': estado_filter,
    }
    return render(request, 'panel_gestor/cocina.html', context)

@staff_member_required
def cambiar_estado_pedido(request, pedido_id, nuevo_estado):
    """
    Acción rápida para mover un pedido de fase.
    """
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    estados_validos = [choice[0] for choice in Pedido.ESTADOS_PEDIDO]
    
    if nuevo_estado in estados_validos:
        pedido.estado = nuevo_estado
        pedido.save()
        messages.success(request, f"Pedido #{pedido.id} actualizado a '{pedido.get_estado_display()}'")
    else:
        messages.error(request, "Estado inválido.")
    
    return redirect('panel_cocina')

@staff_member_required
def api_pedido_detalle(request, pedido_id):
    """
    Devuelve los datos completos de un pedido en JSON.
    """
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    items_data = []
    for item in pedido.items.all():
        items_data.append({
            'producto': item.producto.nombre,
            'cantidad': item.cantidad,
            'precio_unitario': float(item.precio_unitario),
            'subtotal': float(item.get_costo())
        })
        
    data = {
        'id': pedido.id,
        'fecha': pedido.fecha_creacion.strftime("%d/%m/%Y %H:%M"),
        'estado': pedido.get_estado_display(),
        'estado_clave': pedido.estado,
        'total': float(pedido.total),
        'cliente': {
            'nombre': f"{pedido.cliente.first_name} {pedido.cliente.last_name}" or pedido.cliente.username,
            'email': pedido.cliente.email,
            'telefono': pedido.telefono_contacto or "No especificado"
        },
        'envio': {
            'metodo': pedido.metodo_envio_elegido,
            'direccion': pedido.direccion_envio,
            'ciudad': pedido.ciudad_envio,
            'cp': pedido.codigo_postal_envio,
            'costo': float(pedido.costo_envio)
        },
        'items': items_data
    }
    
    return JsonResponse(data)

@staff_member_required
def exportar_comanda_cocina(request):
    """
    Genera un CSV con pedidos listos para cocina.
    """
    pedidos = Pedido.objects.filter(estado='pagado').order_by('fecha_creacion')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="comanda_cocina.csv"'
    
    # BOM para Excel en español
    response.write(u'\ufeff'.encode('utf8'))
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Cliente', 'Detalle del Pedido', 'Notas'])

    for p in pedidos:
        nombre_cliente = f"{p.cliente.first_name} {p.cliente.last_name} ({p.cliente.username})"
        items_str = " + ".join([f"{i.cantidad}x {i.producto.nombre}" for i in p.items.all()])
        
        writer.writerow([
            f"#{p.id}",
            nombre_cliente,
            items_str,
            "Cocinar Urgente"
        ])
        
    return response


# ========================================================
# 4. GESTIÓN DE HORARIOS Y REGLAS (CRUD)
# ========================================================
@staff_member_required
def bloqueos_panel(request):
    """
    Panel para activar/desactivar reglas de disponibilidad.
    """
    reglas = ReglaDisponibilidad.objects.all().order_by('dia_semana', 'hora_inicio')
    
    dias = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
    
    reglas_data = []
    for r in reglas:
        reglas_data.append({
            'id': r.id,
            'dia': dias.get(r.dia_semana, 'Desconocido'),
            'inicio': r.hora_inicio.strftime('%H:%M'),
            'fin': r.hora_fin.strftime('%H:%M'),
            'activa': r.activa
        })

    return render(request, 'panel_gestor/bloqueos.html', {'reglas': reglas_data})

@staff_member_required
@require_POST
def toggle_regla(request, regla_id):
    """Activa o desactiva una regla (AJAX)."""
    regla = get_object_or_404(ReglaDisponibilidad, id=regla_id)
    regla.activa = not regla.activa
    regla.save()
    return JsonResponse({'success': True, 'activa': regla.activa, 'mensaje': 'Regla actualizada'})

@staff_member_required
def regla_editar(request, regla_id=None):
    """Crea o Edita una regla de disponibilidad."""
    if regla_id:
        regla = get_object_or_404(ReglaDisponibilidad, id=regla_id)
        titulo = "Editar Horario"
    else:
        regla = None
        titulo = "Nuevo Horario"

    if request.method == 'POST':
        form = ReglaDisponibilidadForm(request.POST, instance=regla)
        if form.is_valid():
            form.save()
            messages.success(request, "Horario guardado correctamente.")
            return redirect('panel_bloqueos')
    else:
        form = ReglaDisponibilidadForm(instance=regla)

    return render(request, 'panel_gestor/bloqueos_form.html', {'form': form, 'titulo': titulo})

@staff_member_required
def regla_eliminar(request, regla_id):
    """Elimina una regla."""
    regla = get_object_or_404(ReglaDisponibilidad, id=regla_id)
    regla.delete()
    messages.success(request, "Horario eliminado.")
    return redirect('panel_bloqueos')


# ========================================================
# 5. ENVÍOS (LOGÍSTICA)
# ========================================================
@staff_member_required
def envios_panel(request):
    """Tablero logístico."""
    pedidos_activos = Pedido.objects.filter(
        estado__in=['en_preparacion', 'despachado']
    ).order_by('ciudad_envio', 'fecha_creacion')

    total_a_enviar = pedidos_activos.count()
    ciudades_distintas = pedidos_activos.values('ciudad_envio').distinct().count()

    context = {
        'pedidos': pedidos_activos,
        'total_a_enviar': total_a_enviar,
        'ciudades_count': ciudades_distintas,
    }
    return render(request, 'panel_gestor/envios.html', context)


# ========================================================
# 6. PACIENTES (CRM) Y EVOLUCIÓN CLÍNICA
# ========================================================

@staff_member_required
def pacientes_panel(request):
    """
    Lista UNIFICADA de pacientes (Clínicos + Usuarios Web potenciales).
    """
    query = request.GET.get('q')

    # 1. Pacientes ya registrados en el sistema clínico
    pacientes_clinicos = Paciente.objects.all().select_related('usuario')

    # 2. Usuarios web que AÚN NO son pacientes (potenciales)
    usuarios_web_sin_ficha = User.objects.filter(is_staff=False, ficha_paciente__isnull=True)

    if query:
        pacientes_clinicos = pacientes_clinicos.filter(
            Q(nombre__icontains=query) | Q(apellido__icontains=query) | Q(email__icontains=query)
        )
        usuarios_web_sin_ficha = usuarios_web_sin_ficha.filter(
            Q(username__icontains=query) | Q(email__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )

    # 3. Lista Unificada
    lista_final = []

    for p in pacientes_clinicos:
        lista_final.append({
            'tipo': 'PACIENTE',
            'id': p.id,
            'nombre': p.nombre,
            'apellido': p.apellido,
            'email': p.email,
            'telefono': p.telefono,
            'tiene_usuario': p.usuario is not None,
            'inicial': p.nombre[0].upper() if p.nombre else "?"
        })

    for u in usuarios_web_sin_ficha:
        nombre = u.first_name if u.first_name else u.username
        lista_final.append({
            'tipo': 'USUARIO_WEB',
            'id': u.id, # ID del User
            'nombre': nombre,
            'apellido': u.last_name,
            'email': u.email,
            'telefono': None, 
            'tiene_usuario': True,
            'inicial': nombre[0].upper() if nombre else "?"
        })

    context = {'pacientes_lista': lista_final, 'search_query': query}
    return render(request, 'panel_gestor/pacientes_lista.html', context)

@staff_member_required
def crear_paciente(request):
    """
    Crea un nuevo paciente. Opcionalmente crea un usuario web.
    """
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            try:
                paciente = form.save(commit=False)
                email = form.cleaned_data.get('email')
                crear_user = form.cleaned_data.get('crear_usuario')
                
                if crear_user:
                    if User.objects.filter(email=email).exists():
                        messages.info(request, "El usuario web ya existía. Vinculado automáticamente.")
                        paciente.usuario = User.objects.get(email=email)
                    else:
                        nuevo_user = User.objects.create(
                            username=email, email=email,
                            first_name=paciente.nombre, last_name=paciente.apellido,
                            is_active=True
                        )
                        nuevo_user.set_password("Nutri2025")
                        nuevo_user.save()
                        # Crear perfil base
                        if not hasattr(nuevo_user, 'perfil'):
                            Perfil.objects.create(user=nuevo_user, telefono=paciente.telefono)
                        
                        paciente.usuario = nuevo_user
                        messages.success(request, "Usuario web creado (Pass: Nutri2025).")

                paciente.save()
                messages.success(request, f"Paciente {paciente.nombre} registrado.")
                return redirect('panel_pacientes')
            except Exception as e:
                messages.error(request, f"Error: {e}")
    else:
        form = PacienteForm()

    return render(request, 'panel_gestor/paciente_form.html', {'form': form, 'titulo': 'Nuevo Paciente'})

@staff_member_required
def crear_usuario_para_paciente(request, paciente_id):
    """
    Crea un Usuario Web para un paciente existente, recibiendo datos desde un modal.
    """
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    if request.method == 'POST':
        email_form = request.POST.get('email')
        password_form = request.POST.get('password')
        
        if not email_form or not password_form:
            messages.error(request, "El email y la contraseña son obligatorios.")
            return redirect('panel_detalle_paciente', paciente_id=paciente.id)

        try:
            if User.objects.filter(email=email_form).exists():
                usuario_existente = User.objects.get(email=email_form)
                paciente.usuario = usuario_existente
                paciente.email = email_form
                paciente.save()
                messages.info(request, f"Usuario vinculado exitosamente.")
            else:
                nuevo_user = User.objects.create(
                    username=email_form, email=email_form,
                    first_name=paciente.nombre, last_name=paciente.apellido,
                    is_active=True
                )
                nuevo_user.set_password(password_form)
                nuevo_user.save()
                
                if not hasattr(nuevo_user, 'perfil'):
                    Perfil.objects.create(user=nuevo_user, telefono=paciente.telefono)

                paciente.usuario = nuevo_user
                paciente.email = email_form
                paciente.save()
                messages.success(request, f"Usuario web creado exitosamente.")

        except Exception as e:
            messages.error(request, f"Error al crear usuario: {e}")

    return redirect('panel_detalle_paciente', paciente_id=paciente.id)

@staff_member_required
def crear_ficha_desde_usuario(request, user_id):
    """
    Crea una ficha de Paciente para un usuario de Django existente.
    """
    usuario_web = get_object_or_404(User, id=user_id)
    
    if hasattr(usuario_web, 'ficha_paciente'):
        return redirect('panel_detalle_paciente', paciente_id=usuario_web.ficha_paciente.id)

    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save(commit=False)
            paciente.usuario = usuario_web 
            paciente.save()
            messages.success(request, f"Ficha clínica creada.")
            return redirect('panel_detalle_paciente', paciente_id=paciente.id)
    else:
        datos_iniciales = {
            'nombre': usuario_web.first_name or usuario_web.username,
            'apellido': usuario_web.last_name,
            'email': usuario_web.email,
        }
        form = PacienteForm(initial=datos_iniciales)
        # Importante: ocultar el campo de crear usuario porque ya existe
        form.fields['crear_usuario'].widget = forms.HiddenInput()

    return render(request, 'panel_gestor/paciente_form.html', {
        'form': form, 'titulo': f'Crear Ficha para {usuario_web.username}'
    })

@staff_member_required
def detalle_paciente(request, paciente_id):
    """
    Ficha 360° basada en ID de PACIENTE (Clínico).
    Funciona tanto para pacientes Web como Offline.
    """
    paciente_ficha = get_object_or_404(Paciente, id=paciente_id)
    usuario_web = paciente_ficha.usuario

    # 1. Historia Clínica (Consultas)
    consultas_raw = Consulta.objects.filter(paciente=paciente_ficha).order_by('fecha')
    
    labels_grafico = [c.fecha.strftime("%d/%m") for c in consultas_raw]
    data_peso = [float(c.peso_actual) for c in consultas_raw]
    data_grasa = [float(c.porcentaje_grasa) if c.porcentaje_grasa else None for c in consultas_raw]
    data_musculo = [float(c.porcentaje_musculo) if c.porcentaje_musculo else None for c in consultas_raw]

    consultas = consultas_raw.reverse()

    # 2. Datos Comerciales (Pedidos y Turnos)
    pedidos = []
    turnos = []
    total_gastado = 0
    etiquetas = []

    if usuario_web:
        pedidos = Pedido.objects.filter(cliente=usuario_web).order_by('-fecha_creacion')
        total_gastado = pedidos.aggregate(Sum('total'))['total__sum'] or 0
        turnos = TurnoReservado.objects.filter(cliente=usuario_web).order_by('-fecha')
        
        if hasattr(usuario_web, 'perfil'):
            p = usuario_web.perfil
            if p.es_vegetariano: etiquetas.append({'label': 'Vegetariano', 'color': 'success'})
            if p.es_vegano: etiquetas.append({'label': 'Vegano', 'color': 'success'})
            if p.es_celiaco: etiquetas.append({'label': 'Sin TACC', 'color': 'warning'})
    else:
        etiquetas.append({'label': 'Paciente Clínico', 'color': 'secondary'})
        
    # 3. Archivos y Plan (Expediente Digital)
    archivos = ArchivoPaciente.objects.filter(paciente=paciente_ficha).order_by('-fecha_subida')
    ultimo_plan = PlanAlimentacion.objects.filter(paciente=paciente_ficha, activo=True).last()
    
    # Formularios vacíos para los modales
    form_archivo = ArchivoPacienteForm()
    form_plan = PlanAlimentacionForm(initial={'contenido': ultimo_plan.contenido if ultimo_plan else ""})

    context = {
        'paciente': paciente_ficha,
        'usuario_web': usuario_web,
        'consultas': consultas,
        'pedidos': pedidos,
        'turnos': turnos,
        'total_gastado': total_gastado,
        'etiquetas': etiquetas,
        'labels_grafico': labels_grafico,
        'data_peso': data_peso,
        'data_grasa': data_grasa,
        'data_musculo': data_musculo,
        # Nuevos datos de Expediente
        'archivos': archivos,
        'ultimo_plan': ultimo_plan,
        'form_archivo': form_archivo,
        'form_plan': form_plan,
    }
    return render(request, 'panel_gestor/paciente_detalle.html', context)

@staff_member_required
def crear_consulta(request, paciente_id):
    """
    Registra una nueva consulta médica y opcionalmente agenda el próximo turno.
    """
    paciente_ficha = get_object_or_404(Paciente, id=paciente_id)
    
    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        if form.is_valid():
            # 1. Guardar la Consulta Médica (Historial)
            consulta = form.save(commit=False)
            consulta.paciente = paciente_ficha
            consulta.save()
            
            # 2. Lógica para Agendar Próximo Turno (Automático)
            prox_fecha = form.cleaned_data.get('proxima_fecha')
            prox_hora_str = form.cleaned_data.get('proxima_hora')
            
            if prox_fecha and prox_hora_str:
                try:
                    # El turno necesita un User de Django.
                    cliente_user = paciente_ficha.usuario
                    
                    if cliente_user:
                        # Verificamos disponibilidad para no pisar otro turno
                        if not TurnoReservado.objects.filter(fecha=prox_fecha, hora=prox_hora_str, estado='confirmado').exists():
                            TurnoReservado.objects.create(
                                cliente=cliente_user,
                                fecha=prox_fecha,
                                hora=prox_hora_str,
                                estado='confirmado' # Lo creamos ya confirmado porque lo hace el profesional
                            )
                            messages.success(request, f"Consulta guardada y turno agendado para el {prox_fecha}.")
                        else:
                            messages.warning(request, "Consulta guardada, pero el horario del próximo turno ya estaba ocupado.")
                    else:
                        messages.warning(request, "Consulta guardada. No se pudo agendar turno automático porque el paciente no tiene Usuario Web.")
                
                except Exception as e:
                    messages.error(request, f"Error al agendar turno: {e}")
            else:
                messages.success(request, "Consulta guardada correctamente.")

            return redirect('panel_detalle_paciente', paciente_id=paciente_ficha.id)
    else:
        # Pre-llenamos la fecha con "hoy"
        form = ConsultaForm(initial={'fecha': timezone.now().date()})

    return render(request, 'panel_gestor/consulta_form.html', {
        'form': form, 
        'titulo': f'Nueva Consulta: {paciente_ficha.nombre}'
    })


# ========================================================
# 7. GESTIÓN DE INVENTARIO (CRUD)
# ========================================================
@staff_member_required
def inventario_panel(request):
    query = request.GET.get('q')
    productos = Producto.objects.all().order_by('nombre')
    if query:
        productos = productos.filter(Q(nombre__icontains=query) | Q(descripcion__icontains=query))
    return render(request, 'panel_gestor/inventario/lista.html', {'productos': productos, 'search_query': query})

@staff_member_required
def producto_editar(request, producto_id=None):
    obj = get_object_or_404(Producto, id=producto_id) if producto_id else None
    titulo = "Editar Producto" if obj else "Nuevo Producto"
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto guardado.")
            return redirect('panel_inventario')
    else:
        form = ProductoForm(instance=obj)

    return render(request, 'panel_gestor/inventario/formulario.html', {
        'form': form, 'titulo': titulo, 'producto': obj
    })

@staff_member_required
def producto_eliminar(request, producto_id):
    get_object_or_404(Producto, id=producto_id).delete()
    return redirect('panel_inventario')


# ========================================================
# 8. CONFIGURACIÓN Y SUSCRIPCIONES
# ========================================================
@staff_member_required
def configuracion_precios(request):
    """
    Vista para editar los precios globales del sistema.
    """
    config, created = ConfigPrecio.objects.get_or_create(pk=1)
    
    if request.method == 'POST':
        form = ConfigPrecioForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Precios actualizados correctamente.")
            return redirect('panel_configuracion')
    else:
        form = ConfigPrecioForm(instance=config)

    return render(request, 'panel_gestor/configuracion_precios.html', {
        'form': form
    })

@staff_member_required
def extender_suscripcion_manual(request, user_id):
    """
    Suma 30 días de suscripción al usuario manualmente.
    """
    usuario = get_object_or_404(User, id=user_id)
    if not hasattr(usuario, 'perfil'): Perfil.objects.create(user=usuario)
    
    usuario.perfil.extender_suscripcion(dias=30)
    
    messages.success(request, f"Suscripción extendida para {usuario.email}.")
    
    if hasattr(usuario, 'ficha_paciente'):
        return redirect('panel_detalle_paciente', paciente_id=usuario.ficha_paciente.id)
    return redirect('panel_suscripciones') # Vuelve a la lista de suscripciones si venimos de ahí

@staff_member_required
def cancelar_suscripcion_manual(request, user_id):
    """
    Revoca el acceso al recetario inmediatamente.
    """
    usuario = get_object_or_404(User, id=user_id)
    if hasattr(usuario, 'perfil'):
        from datetime import timedelta
        # Vencemos la suscripción ayer
        usuario.perfil.suscripcion_activa_hasta = timezone.now().date() - timedelta(days=1)
        usuario.perfil.save()
        messages.warning(request, f"Suscripción cancelada para {usuario.email}.")
    
    if hasattr(usuario, 'ficha_paciente'):
        return redirect('panel_detalle_paciente', paciente_id=usuario.ficha_paciente.id)
    return redirect('panel_suscripciones')

@staff_member_required
def suscripciones_panel(request):
    """
    Lista de usuarios con suscripción activa o por vencer.
    """
    hoy = timezone.now().date()
    filtro = request.GET.get('filtro', 'activas') 
    
    # Buscamos perfiles (que tienen el dato de suscripción)
    perfiles = Perfil.objects.select_related('user').order_by('suscripcion_activa_hasta')

    if filtro == 'activas':
        perfiles = perfiles.filter(suscripcion_activa_hasta__gte=hoy)
    elif filtro == 'venciendo':
        limite = hoy + timedelta(days=5)
        perfiles = perfiles.filter(suscripcion_activa_hasta__gte=hoy, suscripcion_activa_hasta__lte=limite)
    elif filtro == 'vencidas':
        # Vencidas en el último mes
        limite_pasado = hoy - timedelta(days=30)
        perfiles = perfiles.filter(suscripcion_activa_hasta__lt=hoy, suscripcion_activa_hasta__gte=limite_pasado)

    context = {
        'perfiles': perfiles,
        'filtro_actual': filtro,
        'hoy': hoy
    }
    return render(request, 'panel_gestor/suscripciones.html', context)


# ========================================================
# 9. EXPEDIENTE DIGITAL (ARCHIVOS Y PLANES) - NUEVO
# ========================================================

@staff_member_required
def subir_archivo_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    if request.method == 'POST':
        form = ArchivoPacienteForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.save(commit=False)
            archivo.paciente = paciente
            archivo.save()
            messages.success(request, "Archivo subido correctamente.")
        else:
            messages.error(request, "Error al subir archivo.")
    return redirect('panel_detalle_paciente', paciente_id=paciente.id)

@staff_member_required
def guardar_plan_alimentacion(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    if request.method == 'POST':
        form = PlanAlimentacionForm(request.POST)
        if form.is_valid():
            # Desactivar planes anteriores
            PlanAlimentacion.objects.filter(paciente=paciente).update(activo=False)
            
            plan = form.save(commit=False)
            plan.paciente = paciente
            plan.activo = True
            plan.save()
            messages.success(request, "Plan de alimentación actualizado.")
    return redirect('panel_detalle_paciente', paciente_id=paciente.id)

@staff_member_required
def eliminar_archivo(request, archivo_id):
    archivo = get_object_or_404(ArchivoPaciente, id=archivo_id)
    paciente_id = archivo.paciente.id
    archivo.delete()
    messages.success(request, "Archivo eliminado.")
    return redirect('panel_detalle_paciente', paciente_id=paciente_id)