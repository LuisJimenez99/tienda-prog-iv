from django.shortcuts import render
from django.http import JsonResponse
from .models import Receta
from django.urls import reverse


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

