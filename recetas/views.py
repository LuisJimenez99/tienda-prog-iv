# en recetas/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Receta # Importa tu modelo de receta

@login_required # 1. Requiere que el usuario esté logueado
def vista_recetario(request):
    
    # 2. Verifica si el usuario tiene el permiso en su perfil
    if not request.user.perfil.es_cliente_activo:
        # 3. Si no tiene permiso, lo echamos a la página de inicio
        messages.error(request, "No tienes permiso para acceder a esta sección.")
        return redirect('inicio')
    
    # 4. Si tiene permiso, obtiene todas las recetas y muestra la página
    recetas = Receta.objects.all()
    
    contexto = {
        'recetas': recetas
    }
    return render(request, 'recetas/recetario.html', contexto)