from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Datos de contacto y envío
    telefono = models.CharField(max_length=20, null=True, blank=True)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    ciudad = models.CharField(max_length=100, null=True, blank=True)
    codigo_postal = models.CharField(max_length=10, null=True, blank=True)
    
    # --- PREFERENCIAS DIETARIAS ---
    es_vegetariano = models.BooleanField(default=False, verbose_name="Soy Vegetariano")
    es_vegano = models.BooleanField(default=False, verbose_name="Soy Vegano")
    es_celiaco = models.BooleanField(default=False, verbose_name="Soy Celíaco (Sin TACC)")

    # --- SUSCRIPCIÓN AL RECETARIO (LÓGICA NUEVA) ---
    # Fecha de vencimiento de la suscripción
    suscripcion_activa_hasta = models.DateField(null=True, blank=True, verbose_name="Vencimiento Suscripción")
    
    # Mantenemos la propiedad para compatibilidad con código existente
    # Pero ahora se calcula dinámicamente
    @property
    def es_cliente_activo(self):
        if self.suscripcion_activa_hasta:
            return self.suscripcion_activa_hasta >= timezone.now().date()
        return False

    # Setter para permitir asignación directa (usado en migraciones o admin antiguo)
    @es_cliente_activo.setter
    def es_cliente_activo(self, value):
        if value:
            # Si le ponen True manualmente, damos 30 días por defecto
            self.extender_suscripcion(30)
        else:
            # Si le ponen False, la vencemos ayer
            self.suscripcion_activa_hasta = timezone.now().date() - timedelta(days=1)

    def extender_suscripcion(self, dias=30):
        """
        Suma días a la suscripción actual o empieza una nueva desde hoy.
        """
        hoy = timezone.now().date()
        if self.suscripcion_activa_hasta and self.suscripcion_activa_hasta >= hoy:
            # Si ya tiene una activa, sumamos al final
            self.suscripcion_activa_hasta += timedelta(days=dias)
        else:
            # Si no tiene o ya venció, empieza hoy + días
            self.suscripcion_activa_hasta = hoy + timedelta(days=dias)
        self.save()

    def __str__(self):
        return f"Perfil de {self.user.username}"


# --- SEÑALES (SIGNALS) ---
# Crean el perfil automáticamente cuando se crea un usuario
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.perfil.save()