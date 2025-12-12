from django import forms
from productos.models import Producto
from turnos.models import ReglaDisponibilidad
from .models import Paciente, Consulta  # <-- Importamos Consulta

# --- FORMULARIO DE PRODUCTO (INVENTARIO) ---
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre', 'categoria', 'descripcion', 
            'precio', 'stock', 'imagen', 
            'disponible', 'destacado',
            'es_vegetariano', 'es_vegano', 'es_sin_tacc'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicamos clases CSS modernas a todos los campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-input'})


# --- FORMULARIO DE REGLA DE DISPONIBILIDAD (AGENDA) ---
class ReglaDisponibilidadForm(forms.ModelForm):
    class Meta:
        model = ReglaDisponibilidad
        fields = ['dia_semana', 'hora_inicio', 'hora_fin', 'activa']
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-input'})


# --- FORMULARIO DE PACIENTE (CRM) ---
class PacienteForm(forms.ModelForm):
    # Campo "mágico" para crear usuario de Django opcionalmente
    crear_usuario = forms.BooleanField(
        required=False, 
        initial=False, 
        label="Crear cuenta de acceso a la web",
        help_text="Si marcas esto, se creará un usuario para que el paciente pueda loguearse y comprar."
    )

    class Meta:
        model = Paciente
        fields = ['nombre', 'apellido', 'email', 'telefono', 'fecha_nacimiento', 'observaciones']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-input'})


# --- FORMULARIO DE CONSULTA MÉDICA (NUEVO) ---
class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = [
            'fecha', 'peso_actual', 'altura', 
            'realizo_antropometria',
            'porcentaje_grasa', 'porcentaje_musculo', 
            'cintura', 'cadera', 'sumatoria_pliegues',
            'notas_evolucion'
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'notas_evolucion': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Escribe aquí la evolución del paciente...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Estilos generales
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-input'})
        
        # Atributos especiales para la lógica de Antropometría (JS)
        # Le ponemos una clase especial a los campos "Avanzados"
        campos_antro = ['porcentaje_grasa', 'porcentaje_musculo', 'cintura', 'cadera', 'sumatoria_pliegues']
        for campo in campos_antro:
            self.fields[campo].widget.attrs.update({'class': 'form-input input-antro'})