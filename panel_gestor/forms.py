from django import forms

# Importamos los modelos de las otras apps
from productos.models import Producto
from turnos.models import ReglaDisponibilidad
from configuracion.models import ConfigPrecio # <-- IMPORTANTE: Traer este modelo

# Importamos los modelos de esta app
from .models import Paciente, Consulta, ArchivoPaciente, PlanAlimentacion 


# --- 1. FORMULARIO DE PRODUCTO (INVENTARIO) ---
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
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-input'})


# --- 2. FORMULARIO DE REGLAS (AGENDA) ---
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


# --- 3. FORMULARIO DE PACIENTE (CRM) ---
class PacienteForm(forms.ModelForm):
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


# --- 4. FORMULARIO DE CONSULTA MÉDICA (CON PRÓXIMO TURNO) ---
class ConsultaForm(forms.ModelForm):
    # Campos extra para agendar el siguiente turno automáticamente
    proxima_fecha = forms.DateField(
        required=False, 
        label="Fecha Próxima Cita",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    proxima_hora = forms.CharField( # Usamos CharField para manejarlo con botones o select
        required=False, 
        label="Hora Próxima Cita"
    )

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
        
        # Estilos específicos para los campos nuevos
        self.fields['proxima_fecha'].widget.attrs.update({'class': 'form-input', 'id': 'next-date'})
        self.fields['proxima_hora'].widget.attrs.update({'class': 'form-input', 'id': 'next-time', 'readonly': 'readonly', 'placeholder': 'Selecciona fecha primero'})

        # Atributos especiales para la lógica de Antropometría
        campos_antro = ['porcentaje_grasa', 'porcentaje_musculo', 'cintura', 'cadera', 'sumatoria_pliegues']
        for campo in campos_antro:
            self.fields[campo].widget.attrs.update({'class': 'form-input input-antro'})


# --- 5. FORMULARIO DE PRECIOS (CONFIGURACIÓN - NUEVO) ---
class ConfigPrecioForm(forms.ModelForm):
    class Meta:
        model = ConfigPrecio
        fields = ['precio_consulta', 'precio_recetario_mensual']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})


# --- 6. FORMULARIO DE ARCHIVOS ADJUNTOS (NUEVO) ---
class ArchivoPacienteForm(forms.ModelForm):
    class Meta:
        model = ArchivoPaciente
        fields = ['titulo', 'archivo']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Estilos modernos
        self.fields['titulo'].widget.attrs.update({
            'class': 'form-input', 
            'placeholder': 'Ej: Análisis de sangre 2024'
        })
        self.fields['archivo'].widget.attrs.update({
            'class': 'form-input',
            'accept': 'image/*,.pdf' # Sugerencia visual para el navegador
        })

# --- 7. FORMULARIO DE PLAN DE ALIMENTACIÓN (NUEVO) ---
class PlanAlimentacionForm(forms.ModelForm):
    class Meta:
        model = PlanAlimentacion
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'class': 'form-input diet-editor', # Clase especial para estilizarlo más ancho
                'rows': 15, 
                'placeholder': 'Desayuno:\n- Café con leche\n- 2 tostadas integrales...\n\nAlmuerzo:\n...'
            }),
        }