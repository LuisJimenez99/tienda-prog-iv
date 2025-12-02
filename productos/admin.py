from django.contrib import admin
from .models import Producto, Categoria
from django.utils.html import format_html

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',) 
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    
    # 1. Definimos qué columnas se ven
    list_display = ('vista_previa_imagen', 'nombre', 'categoria', 'precio', 'stock', 'disponible', 'destacado')
    
    # 2. LA SOLUCIÓN: Hacemos que la Imagen Y el Nombre sean enlaces para editar
    list_display_links = ('vista_previa_imagen', 'nombre')
    
    # 3. Definimos qué campos se pueden editar rápido desde la lista
    # (Nota: 'nombre' NO debe estar aquí si está en list_display_links)
    list_editable = ('categoria', 'precio', 'stock', 'disponible', 'destacado')
    
    search_fields = ('nombre', 'descripcion')   
    
    list_filter = ('disponible', 'destacado', 'categoria')

    def vista_previa_imagen(self, obj):
        if obj.imagen:
            # Usamos format_html para renderizar la imagen de forma segura
            return format_html('<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 8px;" />', obj.imagen.url)
        return "Sin Imagen"
    vista_previa_imagen.short_description = 'Imagen'