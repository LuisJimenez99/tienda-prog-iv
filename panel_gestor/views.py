import csv
import json
from datetime import datetime

from django import forms # <-- ¡AQUÍ ESTABA EL FALTANTE!
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
from .models import Paciente, Consulta

# Formularios
from .forms import ProductoForm, ReglaDisponibilidadForm, PacienteForm, ConsultaForm


# ========================================================
# 1. INICIO (DASHBOARD RESUMEN)
# ========================================================
@staff_member_required(login_url='/accounts/login/')
def inicio_panel(request):
    """Dashboard principal: Resumen del día."""
    hoy = timezone.now().date()
    turnos_hoy = TurnoReservado.objects.filter(fecha=hoy, estado='confirmado').count()
    pedidos_pendientes = Pedido.objects.filter(estado='pagado').count()
    
    context = {
        'turnos_hoy': turnos_hoy,
        'pedidos_cocina': pedidos_pendientes,
        'fecha_actual': hoy,
    }
    return render(request, 'panel_gestor/inicio.html', context)


# ========================================================
# 2. AGENDA PROFESIONAL
# ========================================================
@staff_member_required
def agenda_panel(request):
    return render(request, 'panel_gestor/agenda.html')

@staff_member_required
def api_turnos_dia(request):
    date_str = request.GET.get('fecha')
    if not date_str: return JsonResponse({'turnos': []})

    try:
        fecha = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Fecha inválida'}, status=400)

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
            if not nueva_fecha or not nueva_hora:
                return JsonResponse({'success': False, 'error': 'Faltan datos'}, status=400)
            
            turno.fecha = nueva_fecha
            turno.hora = nueva_hora
            if turno.estado == 'cancelado': turno.estado = 'pendiente'
            turno.save()
            mensaje = f"Turno reagendado."
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
    estado_filter = request.GET.get('estado')
    if estado_filter:
        pedidos = Pedido.objects.filter(estado=estado_filter).order_by('-fecha_creacion')
    else:
        pedidos = Pedido.objects.filter(estado__in=['pagado', 'en_preparacion', 'despachado']).order_by('-fecha_creacion')

    context = {'pedidos': pedidos, 'estado_actual': estado_filter}
    return render(request, 'panel_gestor/cocina.html', context)

@staff_member_required
def cambiar_estado_pedido(request, pedido_id, nuevo_estado):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    estados_validos = [choice[0] for choice in Pedido.ESTADOS_PEDIDO]
    
    if nuevo_estado in estados_validos:
        pedido.estado = nuevo_estado
        pedido.save()
        messages.success(request, f"Pedido #{pedido.id} actualizado.")
    else:
        messages.error(request, "Estado inválido.")
    
    return redirect('panel_cocina')

@staff_member_required
def api_pedido_detalle(request, pedido_id):
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
    pedidos = Pedido.objects.filter(estado='pagado').order_by('fecha_creacion')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="comanda_cocina.csv"'
    response.write(u'\ufeff'.encode('utf8'))
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Cliente', 'Detalle del Pedido', 'Notas'])

    for p in pedidos:
        nombre_cliente = f"{p.cliente.first_name} {p.cliente.last_name} ({p.cliente.username})"
        items_str = " + ".join([f"{i.cantidad}x {i.producto.nombre}" for i in p.items.all()])
        writer.writerow([f"#{p.id}", nombre_cliente, items_str, "Cocinar Urgente"])
        
    return response


# ========================================================
# 4. GESTIÓN DE HORARIOS
# ========================================================
@staff_member_required
def bloqueos_panel(request):
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
    regla = get_object_or_404(ReglaDisponibilidad, id=regla_id)
    regla.activa = not regla.activa
    regla.save()
    return JsonResponse({'success': True, 'activa': regla.activa, 'mensaje': 'Regla actualizada'})

@staff_member_required
def regla_editar(request, regla_id=None):
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
            messages.success(request, "Horario guardado.")
            return redirect('panel_bloqueos')
    else:
        form = ReglaDisponibilidadForm(instance=regla)

    return render(request, 'panel_gestor/bloqueos_form.html', {'form': form, 'titulo': titulo})

@staff_member_required
def regla_eliminar(request, regla_id):
    regla = get_object_or_404(ReglaDisponibilidad, id=regla_id)
    regla.delete()
    messages.success(request, "Horario eliminado.")
    return redirect('panel_bloqueos')


# ========================================================
# 5. ENVÍOS
# ========================================================
@staff_member_required
def envios_panel(request):
    pedidos_activos = Pedido.objects.filter(estado__in=['en_preparacion', 'despachado']).order_by('ciudad_envio', 'fecha_creacion')
    total_a_enviar = pedidos_activos.count()
    ciudades_distintas = pedidos_activos.values('ciudad_envio').distinct().count()

    context = {'pedidos': pedidos_activos, 'total_a_enviar': total_a_enviar, 'ciudades_count': ciudades_distintas}
    return render(request, 'panel_gestor/envios.html', context)


# ========================================================
# 6. PACIENTES (CRM)
# ========================================================
@staff_member_required
def pacientes_panel(request):
    query = request.GET.get('q')
    pacientes = User.objects.filter(is_staff=False).select_related('perfil').order_by('-date_joined')

    if query:
        pacientes = pacientes.filter(
            Q(username__icontains=query) | Q(email__icontains=query) |
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )
    context = {'pacientes': pacientes, 'search_query': query}
    return render(request, 'panel_gestor/pacientes_lista.html', context)

@staff_member_required
def crear_paciente(request):
    """Crea un nuevo paciente manual."""
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save(commit=False)
            email = form.cleaned_data['email']
            crear_user = form.cleaned_data['crear_usuario']
            
            if crear_user:
                if User.objects.filter(email=email).exists():
                    messages.warning(request, "El paciente se creó, pero el usuario web ya existía.")
                else:
                    nuevo_user = User.objects.create(username=email, email=email, first_name=paciente.nombre, last_name=paciente.apellido, is_active=True)
                    nuevo_user.set_password("Nutri2025") 
                    nuevo_user.save()
                    paciente.usuario = nuevo_user
                    messages.success(request, "Usuario web creado (Pass: Nutri2025).")

            paciente.save()
            messages.success(request, f"Paciente {paciente.nombre} registrado.")
            return redirect('panel_pacientes')
    else:
        form = PacienteForm()
    return render(request, 'panel_gestor/paciente_form.html', {'form': form, 'titulo': 'Nuevo Paciente'})

@staff_member_required
def detalle_paciente(request, user_id):
    """Ficha 360° del Paciente."""
    paciente_user = get_object_or_404(User, id=user_id)
    try:
        ficha_paciente = paciente_user.ficha_paciente
    except:
        ficha_paciente = None

    consultas = []
    labels_grafico = []
    data_peso = []
    data_grasa = []
    data_musculo = []

    if ficha_paciente:
        consultas_raw = Consulta.objects.filter(paciente=ficha_paciente).order_by('fecha')
        for c in consultas_raw:
            labels_grafico.append(c.fecha.strftime("%d/%m/%y"))
            data_peso.append(float(c.peso_actual))
            data_grasa.append(float(c.porcentaje_grasa) if c.porcentaje_grasa else None)
            data_musculo.append(float(c.porcentaje_musculo) if c.porcentaje_musculo else None)
        consultas = consultas_raw.reverse()

    pedidos = Pedido.objects.filter(cliente=paciente_user).order_by('-fecha_creacion')
    total_gastado = pedidos.aggregate(Sum('total'))['total__sum'] or 0
    turnos = TurnoReservado.objects.filter(cliente=paciente_user).order_by('-fecha')

    etiquetas = []
    if hasattr(paciente_user, 'perfil'):
        if paciente_user.perfil.es_vegetariano: etiquetas.append({'label': 'Vegetariano', 'color': 'success'})
        if paciente_user.perfil.es_vegano: etiquetas.append({'label': 'Vegano', 'color': 'success'})
        if paciente_user.perfil.es_celiaco: etiquetas.append({'label': 'Sin TACC', 'color': 'warning'})

    context = {
        'paciente': paciente_user,
        'ficha_paciente': ficha_paciente,
        'pedidos': pedidos,
        'turnos': turnos,
        'total_gastado': total_gastado,
        'etiquetas': etiquetas,
        'consultas': consultas,
        'labels_grafico': labels_grafico,
        'data_peso': data_peso,
        'data_grasa': data_grasa,
        'data_musculo': data_musculo,
    }
    return render(request, 'panel_gestor/paciente_detalle.html', context)

@staff_member_required
def crear_ficha_desde_usuario(request, user_id):
    """
    Crea una ficha de Paciente para un usuario de Django existente.
    """
    usuario_web = get_object_or_404(User, id=user_id)
    
    if hasattr(usuario_web, 'ficha_paciente'):
        messages.info(request, "Este usuario ya tiene una ficha clínica.")
        return redirect('panel_detalle_paciente', user_id=usuario_web.id)

    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save(commit=False)
            paciente.usuario = usuario_web 
            paciente.save()
            messages.success(request, f"Ficha clínica creada y vinculada a {usuario_web.email}")
            return redirect('panel_detalle_paciente', user_id=usuario_web.id)
    else:
        datos_iniciales = {
            'nombre': usuario_web.first_name,
            'apellido': usuario_web.last_name,
            'email': usuario_web.email,
        }
        form = PacienteForm(initial=datos_iniciales)
        # Aquí usamos 'forms' que ya importamos arriba
        form.fields['crear_usuario'].widget = forms.HiddenInput()

    return render(request, 'panel_gestor/paciente_form.html', {
        'form': form, 'titulo': f'Crear Ficha para {usuario_web.username}'
    })

@staff_member_required
def crear_consulta(request, paciente_id):
    paciente_ficha = get_object_or_404(Paciente, id=paciente_id)
    
    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        if form.is_valid():
            consulta = form.save(commit=False)
            consulta.paciente = paciente_ficha
            consulta.save()
            messages.success(request, "Consulta registrada.")
            if paciente_ficha.usuario:
                return redirect('panel_detalle_paciente', user_id=paciente_ficha.usuario.id)
            else:
                return redirect('panel_pacientes')
    else:
        form = ConsultaForm()

    return render(request, 'panel_gestor/consulta_form.html', {
        'form': form, 'titulo': f'Nueva Consulta: {paciente_ficha.nombre}'
    })


# ========================================================
# 7. INVENTARIO
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
    if producto_id:
        producto = get_object_or_404(Producto, id=producto_id)
        titulo = "Editar Producto"
    else:
        producto = None
        titulo = "Nuevo Producto"

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto guardado.")
            return redirect('panel_inventario')
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'panel_gestor/inventario/formulario.html', {'form': form, 'titulo': titulo, 'producto': producto})

@staff_member_required
def producto_eliminar(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    nombre = producto.nombre
    producto.delete()
    messages.success(request, f"Producto '{nombre}' eliminado.")
    return redirect('panel_inventario')