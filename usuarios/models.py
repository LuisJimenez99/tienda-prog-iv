from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Perfil(models.Model):
    # Enlazamos este perfil con el modelo User de Django.
    # on_delete=models.CASCADE significa que si se borra el usuario, también se borra su perfil.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Campos adicionales que necesitamos
    telefono = models.CharField(max_length=20, null=True, blank=True)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    ciudad = models.CharField(max_length=100, null=True, blank=True)
    codigo_postal = models.CharField(max_length=10, null=True, blank=True)
    
    # Este campo nos servirá en el futuro para dar acceso a contenido exclusivo
    es_cliente_activo = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

# Esta función (llamada "signal") crea un Perfil automáticamente
# cada vez que un nuevo Usuario es creado.
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.perfil.save()
