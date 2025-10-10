from django.shortcuts import render, get_object_or_404
from productos.models import Producto
from recetas.models import Receta
from paginas.models import Pagina # 1. Importamos el modelo 'Pagina'

# --- Vista de Inicio (sin cambios) ---
def inicio(request):
    productos_destacados = Producto.objects.filter(disponible=True, destacado=True)[:3]
    receta_aleatoria = Receta.objects.exclude(imagen__exact='').order_by('?').first()
    contexto = {
        'productos': productos_destacados,
        'receta': receta_aleatoria
    }
    return render(request, "inicio.html", contexto)


# --- 2. VISTA NUEVA PARA LA PÁGINA "SOBRE MÍ" ---
def sobre_mi_view(request):
    """
    Esta vista busca la página estática con el slug 'sobre-mi' y la muestra.
    """
    # 3. Usamos get_object_or_404 para buscar la página de forma segura.
    #    Si no has creado una página con el slug 'sobre-mi' en el admin,
    #    esto mostrará automáticamente un error 404 "Página no encontrada".
    pagina = get_object_or_404(Pagina, slug='sobre-mi')
    
    # 4. Preparamos el contexto para enviar la información de la página al HTML.
    contexto = {
        'pagina': pagina
    }
    
    # 5. Renderizamos la plantilla 'sobre_mi.html' y le pasamos los datos.
    return render(request, 'sobre_mi.html', contexto)

