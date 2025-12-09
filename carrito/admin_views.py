from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDay, ExtractHour, ExtractWeekDay
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Pedido, ItemPedido
from productos.models import Producto

# ... (Las funciones auxiliares obtener_rango_fechas y calcular_crecimiento quedan IGUAL) ...
def obtener_rango_fechas(request):
    hoy = timezone.now()
    inicio_str = request.GET.get('fecha_inicio')
    fin_str = request.GET.get('fecha_fin')

    if inicio_str and fin_str:
        fecha_inicio = datetime.strptime(inicio_str, '%Y-%m-%d')
        fecha_fin = datetime.strptime(fin_str, '%Y-%m-%d')
        fecha_inicio = timezone.make_aware(fecha_inicio)
        fecha_fin = timezone.make_aware(fecha_fin) + timedelta(days=1) - timedelta(seconds=1)
    else:
        fecha_fin = hoy
        fecha_inicio = hoy - timedelta(days=30)
    return fecha_inicio, fecha_fin

def calcular_crecimiento(actual, anterior):
    if anterior == 0:
        return 100 if actual > 0 else 0
    return ((actual - anterior) / anterior) * 100

@staff_member_required
def dashboard_ventas_view(request):
    fecha_inicio, fecha_fin = obtener_rango_fechas(request)
    
    delta = fecha_fin - fecha_inicio
    fecha_inicio_prev = fecha_inicio - delta
    fecha_fin_prev = fecha_inicio

    estados_validos = ['pagado', 'despachado', 'en_preparacion']
    
    pedidos_actuales = Pedido.objects.filter(
        fecha_creacion__range=[fecha_inicio, fecha_fin],
        estado__in=estados_validos
    )
    
    pedidos_previos = Pedido.objects.filter(
        fecha_creacion__range=[fecha_inicio_prev, fecha_fin_prev],
        estado__in=estados_validos
    )

    # --- 1. KPIs ---
    ingresos_actual = pedidos_actuales.aggregate(Sum('total'))['total__sum'] or 0
    ingresos_previo = pedidos_previos.aggregate(Sum('total'))['total__sum'] or 0
    crecimiento_ingresos = calcular_crecimiento(ingresos_actual, ingresos_previo)

    ventas_actual = pedidos_actuales.count()
    ventas_previo = pedidos_previos.count()
    crecimiento_ventas = calcular_crecimiento(ventas_actual, ventas_previo)

    ticket_actual = ingresos_actual / ventas_actual if ventas_actual > 0 else 0
    ticket_previo = ingresos_previo / ventas_previo if ventas_previo > 0 else 0
    crecimiento_ticket = calcular_crecimiento(ticket_actual, ticket_previo)

    # --- 2. VENTAS DIARIAS ---
    ventas_por_dia = pedidos_actuales.annotate(
        dia=TruncDay('fecha_creacion')
    ).values('dia').annotate(total=Sum('total')).order_by('dia')

    labels_dias = [venta['dia'].strftime('%d/%m') for venta in ventas_por_dia]
    data_ingresos_dia = [float(venta['total']) for venta in ventas_por_dia]

    # --- 3. TOP PRODUCTOS ---
    top_productos = ItemPedido.objects.filter(pedido__in=pedidos_actuales).values('producto__nombre').annotate(unidades=Sum('cantidad')).order_by('-unidades')[:5]
    labels_prod = [item['producto__nombre'] for item in top_productos]
    data_prod = [item['unidades'] for item in top_productos]

    # --- 4. NUEVO: VENTAS POR CATEGORÍA (Estandarización) ---
    # Esto funciona para cualquier negocio que use categorías
    ventas_categoria = ItemPedido.objects.filter(
        pedido__in=pedidos_actuales
    ).values('producto__categoria__nombre').annotate(
        total_dinero=Sum(F('cantidad') * F('precio_unitario')) # Calculamos dinero generado
    ).order_by('-total_dinero')

    labels_cat = [v['producto__categoria__nombre'] or 'Sin Categoría' for v in ventas_categoria]
    data_cat = [float(v['total_dinero']) for v in ventas_categoria]

    # --- 5. NUEVO: DÍAS DE LA SEMANA (Patrones de Compra) ---
    # 1=Domingo, 2=Lunes, ... 7=Sábado (depende de la configuración de DB, Django ajusta)
    ventas_semana = pedidos_actuales.annotate(
        dia_semana=ExtractWeekDay('fecha_creacion')
    ).values('dia_semana').annotate(count=Count('id')).order_by('dia_semana')

    # Mapeo de días (Django suele usar Domingo=1, Lunes=2...)
    nombres_dias = {1: 'Dom', 2: 'Lun', 3: 'Mar', 4: 'Mié', 5: 'Jue', 6: 'Vie', 7: 'Sáb'}
    
    # Inicializamos array de 7 días
    data_semana = [0] * 7
    labels_semana = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
    
    for v in ventas_semana:
        # v['dia_semana'] devuelve 1..7. Restamos 1 para el índice 0..6
        idx = (v['dia_semana'] - 1) % 7 
        data_semana[idx] = v['count']

    # --- DATOS EXTRA ---
    stock_critico = Producto.objects.filter(stock__lte=5, disponible=True).order_by('stock')[:5]
    
    top_clientes = pedidos_actuales.values('cliente__username', 'cliente__email').annotate(
        total_gastado=Sum('total'), compras=Count('id')
    ).order_by('-total_gastado')[:5]

    contexto = {
        'title': 'Tablero de Control - NutriTienda',
        'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
        'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
        
        'ingresos_actual': ingresos_actual,
        'crecimiento_ingresos': crecimiento_ingresos,
        'ventas_actual': ventas_actual,
        'crecimiento_ventas': crecimiento_ventas,
        'ticket_actual': ticket_actual,
        'crecimiento_ticket': crecimiento_ticket,
        
        'labels_dias': labels_dias,
        'data_ingresos_dia': data_ingresos_dia,
        
        'labels_prod': labels_prod,
        'data_prod': data_prod,
        
        # Nuevos Contextos
        'labels_cat': labels_cat,
        'data_cat': data_cat,
        'labels_semana': labels_semana,
        'data_semana': data_semana,
        
        'stock_critico': stock_critico,
        'top_clientes': top_clientes,
    }
    
    return render(request, 'admin/dashboard_ventas.html', contexto)