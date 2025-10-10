from django.contrib import admin
from .models import ReglaDisponibilidad, TurnoReservado

# 1. Creamos una clase para personalizar el admin de 'ReglaDisponibilidad'
class ReglaDisponibilidadAdmin(admin.ModelAdmin):
    # En la lista de reglas, mostraremos estas columnas para que sea fácil de leer
    list_display = ('get_dia_semana_display', 'hora_inicio', 'hora_fin', 'activa')
    # Añadimos filtros a la derecha para ver reglas por día o si están activas
    list_filter = ('dia_semana', 'activa')

    # Renombramos el título de la columna para que se vea más amigable
    def get_dia_semana_display(self, obj):
        return obj.get_dia_semana_display()
    get_dia_semana_display.short_description = 'Día de la Semana'


# 2. Creamos una clase para personalizar el admin de 'TurnoReservado'
class TurnoReservadoAdmin(admin.ModelAdmin):
    # Mostraremos esta información en la lista de turnos reservados
    list_display = ('cliente', 'fecha', 'hora', 'estado')
    # Podremos filtrar los turnos por estado y por fecha
    list_filter = ('estado', 'fecha')
    # Añadimos una barra de búsqueda para encontrar turnos por el nombre o email del cliente
    search_fields = ('cliente__username', 'cliente__email')

# 3. Registramos ambos modelos en el sitio de administración
admin.site.register(ReglaDisponibilidad, ReglaDisponibilidadAdmin)
admin.site.register(TurnoReservado, TurnoReservadoAdmin)