from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Perfil

# 1. Definimos un "inline" para el Perfil
class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil de Usuario'
    
    # 2. Definimos los campos. 
    # IMPORTANTE: 'es_cliente_activo' ya no es un campo editable, es una propiedad.
    # Ahora editamos 'suscripcion_activa_hasta'.
    
    fieldsets = (
        ('Datos de Contacto/Envío', {
            'fields': ('telefono', 'direccion', 'ciudad', 'codigo_postal')
        }),
        ('Preferencias Dietarias', {
            'fields': ('es_vegetariano', 'es_vegano', 'es_celiaco')
        }),
        ('Suscripción (Recetario)', {
            'classes': ('collapse',), 
            'description': 'Define hasta cuándo tiene acceso el usuario. Si la fecha es futura, es Activo.',
            # Aquí cambiamos el campo viejo por el nuevo de fecha
            'fields': ('suscripcion_activa_hasta',) 
        }),
    )

# 3. Definimos un nuevo UserAdmin que incluye nuestro PerfilInline
class CustomUserAdmin(BaseUserAdmin):
    inlines = (PerfilInline,)
    
    # Opcional: Mostrar columnas extra en la lista de usuarios
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_suscripcion_status')
    
    def get_suscripcion_status(self, obj):
        # Intentamos acceder al perfil de forma segura
        if hasattr(obj, 'perfil') and obj.perfil.es_cliente_activo:
            return "✅ ACTIVO"
        return "❌ INACTIVO"
    get_suscripcion_status.short_description = "Suscripción"

# 4. Re-registramos el modelo User
admin.site.unregister(User) 
admin.site.register(User, CustomUserAdmin)