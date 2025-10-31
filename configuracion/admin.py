from django.contrib import admin
# Importamos todos los modelos de una vez
from .models import DatosPago, HeroSectionConfig, AparienciaConfig, CarruselImagen
from django.utils.html import format_html

# Admin para los Datos de Pago
@admin.register(DatosPago)
class DatosPagoAdmin(admin.ModelAdmin):
    list_display = ('cbu_alias', 'link_mercado_pago')

# Admin para la Configuración de la Sección Principal
@admin.register(HeroSectionConfig)
class HeroSectionConfigAdmin(admin.ModelAdmin):
    list_display = ('titulo_principal', 'activa', 'imagen_preview')
    list_editable = ('activa',)
    
    fieldsets = (
        (None, {
            'fields': ('activa', 'titulo_principal', 'descripcion', 'imagen_fondo')
        }),
        ('Botón 1 (Izquierda)', {
            'classes': ('collapse',),
            'fields': ('texto_boton_1', 'url_boton_1')
        }),
        ('Botón 2 (Derecha)', {
            'classes': ('collapse',),
            'fields': ('texto_boton_2', 'url_boton_2')
        }),
    )

    def imagen_preview(self, obj):
        if obj.imagen_fondo:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 200px;" />', obj.imagen_fondo.url)
        return "No hay imagen"
    imagen_preview.short_description = 'Previsualización'

    def has_add_permission(self, request):
        if HeroSectionConfig.objects.exists():
            return False
        return True

# Admin para las Imágenes del Carrusel
@admin.register(CarruselImagen)
class CarruselImagenAdmin(admin.ModelAdmin):
    list_display = ('get_imagen_preview', 'titulo', 'orden', 'activo', 'link_url')
    list_editable = ('orden', 'activo',)
    list_filter = ('activo',)
    search_fields = ('titulo',)

    def get_imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="max-height: 75px; max-width: 150px; object-fit: cover;" />', obj.imagen.url)
        return "No hay imagen"
    get_imagen_preview.short_description = "Previsualización"

    fieldsets = (
        (None, {
            'fields': ('activo', 'orden', 'imagen', 'titulo')
        }),
        ('Enlace (Opcional)', {
            'classes': ('collapse',),
            'fields': ('link_url', 'abrir_en_nueva_pestana')
        }),
    )    
    
# Admin para la Configuración de Apariencia
@admin.register(AparienciaConfig)
class AparienciaConfigAdmin(admin.ModelAdmin):
    
    fieldsets = (
        ('Diseño General', {
            'fields': ('color_fondo_body',)
        }),
        ('Página de Inicio: Barra de Navegación (Nav)', {
            'classes': ('collapse',),
            'description': 'Personaliza el logo y los colores del menú de navegación.',
            'fields': (
                'logo_sitio',
                'navbar_color_fondo', 
                'navbar_color_enlaces',
                'color_carrito_activo',
            )
        }),
        ('Página de Inicio: Botones (Globales)', { 
            'classes': ('collapse',),
            'description': 'Define los colores para botones globales (Navbar, Formularios, etc.)',
            'fields': (
                'boton_color_principal_fondo',
                'boton_color_principal_texto',
                'boton_color_principal_hover',
                'boton_color_secundario_borde',
            )
        }),
        ('Página de Inicio: Tarjetas de Productos', {
            'classes': ('collapse',),
            'description': 'Personaliza los colores de las tarjetas de productos.',
            'fields': (
                'tarjeta_color_fondo',
                'tarjeta_color_titulo',
                'tarjeta_color_precio',
            )
        }),
    )

    def has_add_permission(self, request):
        if AparienciaConfig.objects.exists():
            return False
        return True
    
    def has_delete_permission(self, request, obj=None):
        return False