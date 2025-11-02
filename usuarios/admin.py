# usuarios/admin.py

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Perfil

# 1. Definimos un "inline" para el Perfil
class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil de Usuario'
    
    # 2. Definimos los campos del Perfil que queremos ver
    #    (¡Aquí incluimos nuestro "interruptor"!)
    fieldsets = (
        ('Datos de Contacto/Envío', {
            'fields': ('telefono', 'direccion', 'ciudad', 'codigo_postal')
        }),
        ('Permisos Especiales', {
            'classes': ('collapse',), # Lo hace colapsable
            'fields': ('es_cliente_activo',) # <-- ¡EL INTERRUPTOR!
        }),
    )

# 3. Definimos un nuevo UserAdmin que incluye nuestro PerfilInline
class CustomUserAdmin(BaseUserAdmin):
    inlines = (PerfilInline,)

# 4. Re-registramos el modelo User con nuestro admin personalizado
admin.site.unregister(User) # Quitamos el admin viejo de User
admin.site.register(User, CustomUserAdmin) # Añadimos el nuevo