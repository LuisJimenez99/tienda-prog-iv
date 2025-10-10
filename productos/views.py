from django.shortcuts import render, get_object_or_404 # 1. Añadimos la importación de 'get_object_or_404'
from .models import Producto
from django.http import JsonResponse
# Asegúrate de importar Receta si la API está en este archivo
from recetas.models import Receta 

# --- Vista para la lista de productos (sin cambios) ---
def lista_productos(request):
    productos = Producto.objects.filter(disponible=True)
    contexto = {'productos': productos}
    return render(request, 'productos/lista_productos.html', contexto)

# --- 2. VISTA NUEVA PARA EL DETALLE DEL PRODUCTO ---
def detalle_producto(request, producto_id):
    """
    Esta función busca un producto por su ID y muestra su página de detalle.
    """
    # 3. La lógica principal:
    #    'get_object_or_404' es la forma más segura de buscar un objeto.
    #    Intenta encontrar un 'Producto' cuyo 'id' coincida con el 'producto_id' de la URL.
    #    Si no lo encuentra, Django mostrará automáticamente una página de error "404 Not Found".
    producto = get_object_or_404(Producto, id=producto_id)
    
    # 4. Preparamos el contexto (los datos que enviaremos al HTML).
    #    En este caso, solo contiene el producto que encontramos.
    contexto = {
        'producto': producto
    }

    # 5. Renderizamos la nueva plantilla HTML y le pasamos el contexto.
    return render(request, 'productos/detalle_producto.html', contexto)


# --- Vista para la API de recetas (sin cambios) ---
def random_receta_api(request):
    receta = Receta.objects.exclude(imagen__exact='').order_by('?').first()
    if receta:
        data = {
            'nombre': receta.nombre,
            'imagen_url': receta.imagen.url,
            'ingredientes': receta.ingredientes,
            'instrucciones': receta.instrucciones,
            'tiempo_preparacion': receta.tiempo_preparacion,
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'No se encontraron recetas'}, status=404)

