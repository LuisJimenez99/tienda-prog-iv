# configuracion/views.py

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import AparienciaConfig
from .forms import AparienciaConfigForm # Importa el form que acabamos de crear

@staff_member_required # Asegura que solo el staff pueda acceder
def configuracion_apariencia_view(request):
    """
    Esta es la vista personalizada que Django no encontraba.
    Maneja el formulario del dashboard de apariencia.
    """
    
    # Intentamos obtener la única instancia de configuración (pk=1)
    # Si no existe, la creamos.
    config, created = AparienciaConfig.objects.get_or_create(pk=1) 

    if request.method == 'POST':
        # Si el formulario se envía, lo validamos con los datos nuevos
        form = AparienciaConfigForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Configuración de apariencia guardada con éxito!')
            # Redirigir a la misma página para ver los cambios
            return redirect('admin_apariencia')
        else:
            messages.error(request, 'Hubo un error al guardar. Revisa los campos.')
    else:
        # Si es un GET, solo mostramos el formulario con los datos actuales
        form = AparienciaConfigForm(instance=config)

    context = {
        'form': form,
        'title': 'Configuración de Apariencia', # Título para la página
        
        # Variables necesarias para que la plantilla base de Jazzmin funcione
        'site_header': 'Administración TiendaDenu',
        'site_title': 'Admin TiendaDenu',
        'has_permission': request.user.is_staff,
    }
    
    # Renderiza la plantilla HTML que creamos para el dashboard
    return render(request, 'admin/configuracion/apariencia_dashboard.html', context)