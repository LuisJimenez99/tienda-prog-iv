from django.contrib import admin
from .models import Receta

class RecetaAdmin(admin.ModelAdmin):
    
    list_display = ('nombre', 'tiempo_preparacion')

admin.site.register(Receta, RecetaAdmin)