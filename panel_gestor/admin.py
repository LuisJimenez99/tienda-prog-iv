from django.contrib import admin
from .models import Paciente, Consulta

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'email', 'tiene_usuario_web', 'fecha_creacion')
    search_fields = ('nombre', 'apellido', 'email')
    
    def tiene_usuario_web(self, obj):
        return obj.usuario is not None
    tiene_usuario_web.boolean = True
    tiene_usuario_web.short_description = "¿Tiene Usuario Web?"

@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'fecha', 'peso_actual', 'imc')
    list_filter = ('fecha',)