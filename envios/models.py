from django.db import models

class MetodoEnvio(models.Model):
    nombre = models.CharField(max_length=100, help_text="Ej: Correo Argentino (Domicilio)")
    descripcion = models.CharField(max_length=255, help_text="Ej: Entrega 3-5 días hábiles", blank=True)
    activo = models.BooleanField(default=True, help_text="Marcar para mostrar este método a los clientes.")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Método de Envío"
        verbose_name_plural = "Métodos de Envío"

class RangoPostal(models.Model):
    metodo = models.ForeignKey(MetodoEnvio, related_name='rangos', on_delete=models.CASCADE)
    cp_desde = models.PositiveIntegerField(help_text="Código postal inicial del rango (ej: 1000)")
    cp_hasta = models.PositiveIntegerField(help_text="Código postal final del rango (ej: 1900)")
    precio = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio específico para este rango.")

    def __str__(self):
        return f"{self.metodo.nombre}: {self.cp_desde} - {self.cp_hasta} (${self.precio})"

    class Meta:
        verbose_name = "Rango Postal"
        verbose_name_plural = "Rangos Postales"
        ordering = ['cp_desde']