from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, PerfilUpdateForm

# --- Vista para mostrar la página de perfil del usuario ---
@login_required
def profile_view(request):
    # Simplemente renderiza la plantilla del perfil.
    # El decorador @login_required se asegura de que solo los usuarios
    # que han iniciado sesión puedan ver esta página.
    return render(request, 'usuarios/profile.html')

# --- Vista para editar el perfil del usuario ---
@login_required
def edit_profile_view(request):
    # request.method == 'POST' se cumple cuando el usuario hace clic en "Guardar Cambios"
    if request.method == 'POST':
        # Cargamos los datos enviados en los formularios, vinculándolos al usuario actual
        user_form = UserUpdateForm(request.POST, instance=request.user)
        perfil_form = PerfilUpdateForm(request.POST, instance=request.user.perfil)
        
        # Verificamos si ambos formularios son válidos
        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save() # Guardamos los cambios en el modelo User
            perfil_form.save() # Guardamos los cambios en el modelo Perfil
            messages.success(request, '¡Tu perfil ha sido actualizado exitosamente!')
            return redirect('profile') # Redirigimos de vuelta a la página de perfil
    else:
        # Si la página se carga por primera vez (método GET),
        # mostramos los formularios con la información actual del usuario.
        user_form = UserUpdateForm(instance=request.user)
        perfil_form = PerfilUpdateForm(instance=request.user.perfil)

    contexto = {
        'user_form': user_form,
        'perfil_form': perfil_form
    }

    return render(request, 'usuarios/edit_profile.html', contexto)

