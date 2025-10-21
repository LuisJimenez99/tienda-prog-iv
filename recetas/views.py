from django.shortcuts import render
from django.http import JsonResponse
from .models import Receta
from django.urls import reverse

# --- VISTA DE API PARA LA RECETA ALEATORIA ---
def random_receta_api(request):
    # Buscamos una receta al azar que tenga una imagen cargada
    receta = Receta.objects.exclude(imagen__exact='').order_by('?').first()

    if receta:
        # Preparamos los datos que el JavaScript necesita
        data = {
            'nombre': receta.nombre,
            'imagen_url': receta.imagen.url,
            'ingredientes': receta.ingredientes,
            'instrucciones': receta.instrucciones,
            'tiempo_preparacion': receta.tiempo_preparacion,
        }
        return JsonResponse(data)
    else:
        # En caso de que no haya recetas, devolvemos un error
        return JsonResponse({'error': 'No se encontraron recetas'}, status=404)

