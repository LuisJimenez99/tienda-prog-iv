from django.contrib import admin
from .models import Receta

# Creamos una clase para personalizar cómo se ve el admin
class RecetaAdmin(admin.ModelAdmin):
    # En la lista de recetas, mostraremos estas dos columnas
    list_display = ('nombre', 'tiempo_preparacion')

# Registramos el modelo 'Receta' en el admin, usando la personalización de arriba
admin.site.register(Receta, RecetaAdmin)