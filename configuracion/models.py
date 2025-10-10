from django.db import models

# Create your models here.
from django.db import models

class DatosPago(models.Model):
        cbu_alias = models.CharField(max_length=255, help_text="Tu CBU o Alias para transferencias.")
        link_mercado_pago = models.URLField(max_length=400, help_text="El enlace de pago de Mercado Pago.")

        def __str__(self):
            return "Datos de Pago"

        class Meta:
            verbose_name = "Datos de Pago"
    