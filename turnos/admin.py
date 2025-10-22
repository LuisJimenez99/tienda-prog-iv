from django.contrib import admin
from .models import ReglaDisponibilidad, TurnoReservado


class ReglaDisponibilidadAdmin(admin.ModelAdmin):

    list_display = ('get_dia_semana_display', 'hora_inicio', 'hora_fin', 'activa')
    
    list_filter = ('dia_semana', 'activa')

    def get_dia_semana_display(self, obj):
        return obj.get_dia_semana_display()
    get_dia_semana_display.short_description = 'Día de la Semana'



class TurnoReservadoAdmin(admin.ModelAdmin):
    
    list_display = ('cliente', 'fecha', 'hora', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('cliente__username', 'cliente__email')
admin.site.register(ReglaDisponibilidad, ReglaDisponibilidadAdmin)
admin.site.register(TurnoReservado, TurnoReservadoAdmin)