from django.contrib import admin
from .models import ReglaDisponibilidad, TurnoReservado

@admin.register(ReglaDisponibilidad)
class ReglaDisponibilidadAdmin(admin.ModelAdmin):
    list_display = ('dia_semana_display', 'hora_inicio', 'hora_fin', 'activa')
    list_filter = ('dia_semana', 'activa')

    def dia_semana_display(self, obj):
        return obj.get_dia_semana_display()
    dia_semana_display.short_description = 'Día de la Semana'

@admin.register(TurnoReservado)
class TurnoReservadoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'fecha', 'hora', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('cliente__username', 'cliente__email')
    
    list_editable = ['estado']