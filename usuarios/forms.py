from django import forms
from django.contrib.auth.models import User
from .models import Perfil

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        
class PerfilUpdateForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = [
            'telefono', 'direccion', 'ciudad', 'codigo_postal',
            # Añadimos los checkboxes
            'es_vegetariano', 'es_vegano', 'es_celiaco'
        ]
        widgets = {
            'es_vegetariano': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'es_vegano': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'es_celiaco': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }