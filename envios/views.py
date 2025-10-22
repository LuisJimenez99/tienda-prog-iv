from django.http import JsonResponse
from .models import RangoPostal, MetodoEnvio
from django.db.models import Q

def calcular_envio_api(request):
    cp_str = request.GET.get('cp')

    if not cp_str:
        return JsonResponse({'error': 'No se proporcionó código postal'}, status=400)

    try:
        cp = int(cp_str)
    except ValueError:
        return JsonResponse({'error': 'Código postal inválido'}, status=400)

    # Buscamos en la base de datos los rangos que coincidan
    # y que pertenezcan a un método de envío activo
    rangos = RangoPostal.objects.filter(
        Q(cp_desde__lte=cp) & Q(cp_hasta__gte=cp),
        metodo__activo=True
    ).order_by('precio')

    if not rangos.exists():
        return JsonResponse(
            {'error': 'No hay métodos de envío disponibles para este código postal.'},
            status=404
        )

    # Construimos la respuesta
    metodos = []
    for rango in rangos:
        metodos.append({
            'nombre': rango.metodo.nombre,
            'descripcion': rango.metodo.descripcion,
            # Formateamos el precio como moneda (ej: $ 5.000,00)
            'precio': f"${rango.precio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        })

    return JsonResponse({'metodos': metodos})
