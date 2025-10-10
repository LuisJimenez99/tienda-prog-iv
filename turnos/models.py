from django.db import models
from django.contrib.auth.models import User

class ReglaDisponibilidad(models.Model):
    DIAS_SEMANA = [
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'),
        (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo'),
    ]
    dia_semana = models.IntegerField(choices=DIAS_SEMANA, help_text="Elige el día de la semana para esta regla.")
    hora_inicio = models.TimeField(help_text="Formato: HH:MM")
    hora_fin = models.TimeField(help_text="Formato: HH:MM")
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"Regla para los {self.get_dia_semana_display()} de {self.hora_inicio.strftime('%H:%M')} a {self.hora_fin.strftime('%H:%M')}"

    class Meta:
        verbose_name = "Regla de Disponibilidad"
        verbose_name_plural = "Reglas de Disponibilidad"

class TurnoReservado(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente de Pago'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
    )
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Turno de {self.cliente.username} el {self.fecha.strftime('%d/%m/%Y')} a las {self.hora.strftime('%H:%M')}"

    class Meta:
        verbose_name = "Turno Reservado"
        verbose_name_plural = "Turnos Reservados"

