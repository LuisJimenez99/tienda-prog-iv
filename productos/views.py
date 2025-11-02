# productos/views.py

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from .models import Producto, Categoria
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger # <-- 1. IMPORTAR PAGINATOR

def lista_productos(request):
    # Obtenemos todos los productos (query base)
    productos_list = Producto.objects.filter(disponible=True).order_by('nombre') # Es bueno ordenar
    categorias = Categoria.objects.all()
    
    # --- Aplicamos Filtros (Búsqueda y Categoría) ---
    query = request.GET.get('q')
    if query:
        productos_list = productos_list.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query)
        )
    
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        productos_list = productos_list.filter(categoria__id=categoria_id)
    
    # --- 2. LÓGICA DE PAGINACIÓN ---
    paginator = Paginator(productos_list, 12) # Muestra 12 productos por página
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        # Si la página no es un entero, muestra la primera página.
        page_obj = paginator.get_page(1)
    except EmptyPage:
        # Si la página está fuera de rango (ej. 9999), muestra la última página.
        page_obj = paginator.get_page(paginator.num_pages)
    
    # --- 3. CONTEXTO ACTUALIZADO ---
    contexto = { 
        'productos': page_obj, # <-- Pasamos el 'page_obj' en lugar de 'productos_list'
        'categorias': categorias, 
    }
    return render(request, 'productos/lista_productos.html', contexto)

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    contexto = { 'producto': producto }
    return render(request, 'productos/detalle_producto.html', contexto)

def live_search_api(request):
    query = request.GET.get('q', '')
    productos_sugeridos = []
    if query and len(query) > 2:
        productos = Producto.objects.filter(nombre__icontains=query, disponible=True)[:5]
        for producto in productos:
            productos_sugeridos.append({
                'id': producto.id,
                'nombre': producto.nombre,
                'url': reverse('detalle_producto', args=[producto.id]), 
                'imagen_url': producto.imagen.url if producto.imagen else ''
            })
    return JsonResponse({'productos': productos_sugeridos})