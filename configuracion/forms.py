from django import forms
from .models import AparienciaConfig
from colorfield.widgets import ColorWidget # Para mostrar el selector de color

class AparienciaConfigForm(forms.ModelForm):
    class Meta:
        model = AparienciaConfig
        fields = '__all__' # Incluye todos los campos del modelo
        widgets = {
            # Asegura que los campos de color usen el widget correcto
            'color_fondo_body': ColorWidget,
            'navbar_color_fondo': ColorWidget,
            'navbar_color_enlaces': ColorWidget,
            'boton_color_principal_fondo': ColorWidget,
            'boton_color_principal_texto': ColorWidget,
            'boton_color_principal_hover': ColorWidget,
            'boton_color_secundario_borde': ColorWidget,
            'color_titulo_tarjeta': ColorWidget,
            'color_desc_tarjeta': ColorWidget,
            'card_btn_principal_fondo': ColorWidget,
            'card_btn_principal_texto': ColorWidget,
            'card_btn_principal_hover': ColorWidget,
            'card_btn_secundario_borde': ColorWidget,
        }

    # Opcional: Puedes organizar los campos en el formulario si quieres
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ejemplo: podrías añadir placeholders o clases CSS aquí si tu plantilla lo necesita
        # for field_name, field in self.fields.items():
        #     field.widget.attrs.update({'class': 'form-control'})