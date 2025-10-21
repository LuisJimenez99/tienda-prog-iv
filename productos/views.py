from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from .models import Producto, Categoria
from django.urls import reverse # <-- ¡ESTA ES LA LÍNEA QUE FALTABA!

# ... (tu vista lista_productos y detalle_producto se quedan como están) ...

def lista_productos(request):
    productos = Producto.objects.filter(disponible=True)
    categorias = Categoria.objects.all()
    query = request.GET.get('q')
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query)
        )
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        productos = productos.filter(categoria__id=categoria_id)
    contexto = { 'productos': productos, 'categorias': categorias, }
    return render(request, 'productos/lista_productos.html', contexto)

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    contexto = { 'producto': producto }
    return render(request, 'productos/detalle_producto.html', contexto)


# --- VISTA DE API PARA LA BÚSQUEDA EN VIVO ---
def live_search_api(request):
    query = request.GET.get('q', '')
    productos_sugeridos = []
    if query and len(query) > 2:
        productos = Producto.objects.filter(nombre__icontains=query, disponible=True)[:5]
        for producto in productos:
            productos_sugeridos.append({
                'id': producto.id,
                'nombre': producto.nombre,
                'url': reverse('detalle_producto', args=[producto.id]), # Ahora 'reverse' está definido
                'imagen_url': producto.imagen.url if producto.imagen else ''
            })
    return JsonResponse({'productos': productos_sugeridos})