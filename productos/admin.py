from django.contrib import admin
from .models import Producto, Categoria
from django.utils.html import format_html


class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',) 
    prepopulated_fields = {'slug': ('nombre',)}


class ProductoAdmin(admin.ModelAdmin):
    
    list_display = ('vista_previa_imagen', 'nombre', 'categoria', 'precio', 'stock', 'disponible', 'destacado')
    
    list_editable = ('categoria', 'precio', 'stock', 'disponible', 'destacado')
    
    search_fields = ('nombre', 'descripcion')   
    
    list_filter = ('disponible', 'destacado', 'categoria')

    def vista_previa_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 8px;" />', obj.imagen.url)
        return "Sin Imagen"
    vista_previa_imagen.short_description = 'Imagen'


admin.site.register(Producto, ProductoAdmin)
admin.site.register(Categoria, CategoriaAdmin)

