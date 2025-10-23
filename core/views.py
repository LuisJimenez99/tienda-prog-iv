from django.shortcuts import render, get_object_or_404
from productos.models import Producto
from recetas.models import Receta
from paginas.models import Pagina
# --- IMPORTACIÓN NUEVA ---
from configuracion.models import HeroSectionConfig

# --- VISTA DE INICIO (ACTUALIZADA) ---
def inicio(request):
    # Lógica que ya teníamos:
    productos_destacados = Producto.objects.filter(disponible=True, destacado=True)[:3]
    receta_aleatoria = Receta.objects.exclude(imagen__exact='').order_by('?').first()

    # --- LÓGICA NUEVA (Paso 3) ---
    # Buscamos la configuración activa para la sección principal
    hero_config = HeroSectionConfig.objects.filter(activa=True).first()

    contexto = {
        'productos': productos_destacados,
        'receta': receta_aleatoria,
        'hero_config': hero_config, # <-- Añadimos la nueva configuración al contexto
    }
    return render(request, "inicio.html", contexto)

# --- VISTA "SOBRE MÍ" (Sin cambios) ---
def sobre_mi_view(request):
    pagina = get_object_or_404(Pagina, slug='sobre-mi')
    contexto = {
        'pagina': pagina
    }
    return render(request, 'sobre_mi.html', contexto)

