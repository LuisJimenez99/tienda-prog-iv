from django.shortcuts import render, get_object_or_404
from productos.models import Producto
from recetas.models import Receta
from paginas.models import Pagina
from configuracion.models import HeroSectionConfig, CarruselImagen # <-- 1. Importa CarruselImagen


def inicio(request):
    # Lógica que ya teníamos:
    productos_destacados = Producto.objects.filter(disponible=True, destacado=True)[:3]
    receta_aleatoria = Receta.objects.exclude(imagen__exact='').order_by('?').first()
    hero_config = HeroSectionConfig.objects.filter(activa=True).first()

    # --- LÓGICA NUEVA (Paso 4) ---
    # Buscamos las imágenes del carrusel que estén activas y las ordenamos
    imagenes_carrusel = CarruselImagen.objects.filter(activo=True).order_by('orden')

    contexto = {
        'productos': productos_destacados,
        'receta': receta_aleatoria,
        'hero_config': hero_config,
        'imagenes_carrusel': imagenes_carrusel, # <-- 2. Añadimos las imágenes al contexto
    }
    return render(request, "inicio.html", contexto)

# --- VISTA "SOBRE MÍ" (Sin cambios) ---
def sobre_mi_view(request):
    pagina = get_object_or_404(Pagina, slug='sobre-mi')
    contexto = {
        'pagina': pagina
    }
    return render(request, 'sobre_mi.html', contexto)

