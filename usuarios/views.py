from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Importaciones para el sistema de activación de cuenta
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site

# --- VISTA DE REGISTRO CON ACTIVACIÓN ---
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            
            current_site = get_current_site(request)
            mail_subject = 'Activa tu cuenta de NutriTienda'
            message = render_to_string('usuarios/activation_email_body.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            
            return redirect('register_done')
        else:
            messages.error(request, "Por favor, corrige los errores a continuación.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'usuarios/register.html', {'form': form})

# --- VISTA DE ACTIVACIÓN DE CUENTA ---
def activate_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, '¡Felicidades! Tu cuenta ha sido activada y has iniciado sesión.')
        return redirect('register_complete')
    else:
        messages.error(request, 'El enlace de activación es inválido.')
        return redirect('inicio')

# --- VISTA DE LOGIN SEGURA (ACTUALIZADA) ---
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('inicio')
                else:
                    messages.error(request, "Esta cuenta está inactiva. Por favor, verifica tu email para activarla.")
            else:
                messages.error(request, "Usuario o contraseña incorrectos.")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
            
    form = AuthenticationForm()
    return render(request, 'usuarios/login.html', {'form': form})

# --- VISTA DE CIERRE DE SESIÓN ---
def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión exitosamente.")
    return redirect('inicio')

# --- VISTA DE PERFIL ---
@login_required
def profile_view(request):
    return render(request, 'usuarios/profile.html')

