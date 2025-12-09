from django.db import models
from django.contrib.auth.models import User # <-- Importar User
from django.urls import reverse
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit, Transpose

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural = "Categorías"

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    
    imagen = ProcessedImageField(
        upload_to='productos/',
        processors=[Transpose(), ResizeToFit(width=1024, height=1024)],
        format='WEBP',
        options={'quality': 85},
        blank=True, null=True
    )
    
    stock = models.PositiveIntegerField(default=0, help_text="Cantidad disponible en inventario")
    disponible = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)

    # --- NUEVAS ETIQUETAS NUTRICIONALES ---
    es_vegetariano = models.BooleanField(default=False, verbose_name="Apto Vegetariano")
    es_vegano = models.BooleanField(default=False, verbose_name="Apto Vegano")
    es_sin_tacc = models.BooleanField(default=False, verbose_name="Apto Celíaco (Sin TACC)")

    # --- LISTA DE DESEOS (FAVORITOS) ---
    # Esta es la línea que faltaba en tu base de datos
    favoritos = models.ManyToManyField(User, related_name='productos_favoritos', blank=True)

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('detalle_producto', args=[self.id])