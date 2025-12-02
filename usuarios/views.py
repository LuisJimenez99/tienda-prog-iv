from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, PerfilUpdateForm
from carrito.models import Pedido # <-- Importamos el modelo Pedido

# --- Vista para mostrar la página de perfil del usuario ---
@login_required
def profile_view(request):
    # 1. Buscamos los pedidos de este cliente
    # Los ordenamos por fecha de creación descendente (el más nuevo primero)
    pedidos = Pedido.objects.filter(cliente=request.user).order_by('-fecha_creacion')

    contexto = {
        'pedidos': pedidos
    }
    return render(request, 'usuarios/profile.html', contexto)

# --- Vista para editar el perfil del usuario ---
@login_required
def edit_profile_view(request):
    # ... (Esta función queda IGUAL que antes) ...
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        perfil_form = PerfilUpdateForm(request.POST, instance=request.user.perfil)
        
        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save()
            perfil_form.save()
            messages.success(request, '¡Tu perfil ha sido actualizado exitosamente!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        perfil_form = PerfilUpdateForm(instance=request.user.perfil)

    contexto = {
        'user_form': user_form,
        'perfil_form': perfil_form
    }

    return render(request, 'usuarios/edit_profile.html', contexto)