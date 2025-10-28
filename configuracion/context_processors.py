from .models import AparienciaConfig

def apariencia_context(request):
    config = AparienciaConfig.objects.first()
    
    if not config:
        # Valores por defecto si aún no has guardado nada en el admin
        config_data = {
            'color_fondo_body': '#ECF0E5',
            'navbar_color_fondo': '#FFFFFF',
            'navbar_color_enlaces': '#555555',
            'boton_color_principal_fondo': '#78857A',
            'boton_color_principal_texto': '#FFFFFF',
            'boton_color_principal_hover': '#647066',
            'boton_color_secundario_borde': '#78857A',
        }
    else:
        config_data = config
        
    return {'apariencia_config': config_data}