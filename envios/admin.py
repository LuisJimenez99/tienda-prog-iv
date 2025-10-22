from django.contrib import admin
from .models import MetodoEnvio, RangoPostal

# Esta clase permite editar 'RangoPostal' DENTRO de 'MetodoEnvio'
class RangoPostalInline(admin.TabularInline):
    model = RangoPostal
    extra = 1 # Muestra 1 campo vacío para añadir un nuevo rango
    verbose_name = "Rango de precio por Código Postal"
    verbose_name_plural = "Rangos de precios por Código Postal"

@admin.register(MetodoEnvio)
class MetodoEnvioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    
    # Aquí conectamos los rangos postales
    inlines = [RangoPostalInline]

# Opcional: Registra RangoPostal para verlo por separado si quieres
@admin.register(RangoPostal)
class RangoPostalAdmin(admin.ModelAdmin):
    list_display = ('metodo', 'cp_desde', 'cp_hasta', 'precio')
    list_filter = ('metodo',)