from django.contrib import admin
from .models import DatosPago, HeroSectionConfig, AparienciaConfig  # Importamos AMBOS modelos
from django.utils.html import format_html
from .models import CarruselImagen # Asegúrate de importar el nuevo modelo
from django.utils.html import format_html # Necesario para la previsualización

 
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
    
@admin.register(CarruselImagen)
class CarruselImagenAdmin(admin.ModelAdmin):
    list_display = ('get_imagen_preview', 'titulo', 'orden', 'activo', 'link_url')
    # Hacemos que 'orden' y 'activo' se puedan editar directamente en la lista
    list_editable = ('orden', 'activo',)
    list_filter = ('activo',)
    search_fields = ('titulo',)

    def get_imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="max-height: 75px; max-width: 150px; object-fit: cover;" />', obj.imagen.url)
        return "No hay imagen"
    get_imagen_preview.short_description = "Previsualización"

    # Organizamos los campos en el formulario de edición
    fieldsets = (
        (None, {
            'fields': ('activo', 'orden', 'imagen', 'titulo')
        }),
        ('Enlace (Opcional)', {
            'classes': ('collapse',), # Lo hace colapsable
            'fields': ('link_url', 'abrir_en_nueva_pestana')
        }),
    )    
    
from django.contrib import admin
from .models import DatosPago, HeroSectionConfig, AparienciaConfig 
from django.utils.html import format_html

# ... (Tu 'DatosPagoAdmin' y 'HeroSectionConfigAdmin' se quedan igual) ...

@admin.register(AparienciaConfig)
class AparienciaConfigAdmin(admin.ModelAdmin):
    
    # --- ¡AQUÍ CREAMOS LA JERARQUÍA! ---
    fieldsets = (
        (None, {
            'fields': ('color_fondo_body',)
        }),
        ('Página de Inicio: Barra de Navegación (Nav)', {
            'classes': ('collapse',), # Esto lo hace colapsable
            'fields': (
                'navbar_color_fondo', 
                'navbar_color_enlaces',
            )
        }),
        ('Página de Inicio: Botones (Global)', {
            'classes': ('collapse',),
            'description': 'Define los colores para todos los botones del sitio (Nav, Tarjetas, etc.)',
            'fields': (
                'boton_color_principal_fondo',
                'boton_color_principal_texto',
                'boton_color_principal_hover',
                'boton_color_secundario_borde',
            )
        }),
    )

    # ... (El resto de las funciones 'has_add_permission' y 'has_delete_permission' se quedan igual) ...
    def has_add_permission(self, request):
        if AparienciaConfig.objects.exists():
            return False
        return True
    def has_delete_permission(self, request, obj=None):
        return False