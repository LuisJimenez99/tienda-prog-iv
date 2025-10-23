from django.contrib import admin
from .models import DatosPago, HeroSectionConfig # Importamos AMBOS modelos
from django.utils.html import format_html

# Admin para los Datos de Pago (que ya tenías)
@admin.register(DatosPago)
class DatosPagoAdmin(admin.ModelAdmin):
    list_display = ('cbu_alias', 'link_mercado_pago')

# --- CÓDIGO NUEVO ---
# Admin para la nueva Configuración de la Sección Principal
@admin.register(HeroSectionConfig)
class HeroSectionConfigAdmin(admin.ModelAdmin):
    list_display = ('titulo_principal', 'activa', 'imagen_preview')
    list_editable = ('activa',)
    
    # Agrupamos los campos en el formulario de edición para que sea más ordenado
    fieldsets = (
        (None, {
            'fields': ('activa', 'titulo_principal', 'descripcion', 'imagen_fondo')
        }),
        ('Botón 1 (Izquierda)', {
            'classes': ('collapse',), # Opcional: hace que la sección se pueda colapsar
            'fields': ('texto_boton_1', 'url_boton_1')
        }),
        ('Botón 2 (Derecha)', {
            'classes': ('collapse',),
            'fields': ('texto_boton_2', 'url_boton_2')
        }),
    )

    # Función para mostrar una miniatura de la imagen en la lista del admin
    def imagen_preview(self, obj):
        if obj.imagen_fondo:
            # Mostramos una imagen pequeña
            return format_html('<img src="{}" style="max-height: 100px; max-width: 200px;" />', obj.imagen_fondo.url)
        return "No hay imagen"
    imagen_preview.short_description = 'Previsualización'

    # Para asegurarnos de que solo haya una configuración
    def has_add_permission(self, request):
        # Si ya existe una configuración, no permitimos añadir más
        if HeroSectionConfig.objects.exists():
            return False
        return True