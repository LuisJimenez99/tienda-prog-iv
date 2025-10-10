from django.contrib import admin
# 1. Importamos los dos modelos desde models.py: Producto y Categoria
from .models import Producto, Categoria
from django.utils.html import format_html

# 2. Creamos una clase de administración para el nuevo modelo Categoria
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',) # En la lista de categorías, solo mostraremos el nombre.
    
    # Esta es una función muy útil: rellena automáticamente el campo 'slug'
    # mientras escribes el 'nombre', creando una URL amigable (ej: "Postres Saludables" -> "postres-saludables").
    prepopulated_fields = {'slug': ('nombre',)}

# 3. Actualizamos la clase de administración para Producto
class ProductoAdmin(admin.ModelAdmin):
    # Añadimos 'categoria' a la lista de columnas visibles
    list_display = ('vista_previa_imagen', 'nombre', 'categoria', 'precio', 'stock', 'disponible', 'destacado')
    
    # Hacemos que la categoría también se pueda editar directamente desde la lista
    list_editable = ('categoria', 'precio', 'stock', 'disponible', 'destacado')
    
    search_fields = ('nombre', 'descripcion')
    
    # Añadimos 'categoria' a los filtros de la derecha
    list_filter = ('disponible', 'destacado', 'categoria')

    def vista_previa_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 8px;" />', obj.imagen.url)
        return "Sin Imagen"
    vista_previa_imagen.short_description = 'Imagen'

# 4. Registramos ambos modelos en el sitio de administración
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Categoria, CategoriaAdmin)

