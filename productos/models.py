# productos/models.py
from django.db import models

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
    
    # Campo de imagen corregido:
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    
    stock = models.PositiveIntegerField(default=0, help_text="Cantidad disponible en inventario")
    disponible = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    def __str__(self):
        return self.nombre