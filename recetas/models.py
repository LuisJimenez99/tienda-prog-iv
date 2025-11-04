# recetas/models.py
from django.db import models

class Receta(models.Model):
    nombre = models.CharField(max_length=150)
    
    # Campo de imagen corregido:
    imagen = models.ImageField(upload_to='recetas/', blank=True, null=True)
    
    ingredientes = models.TextField(help_text="Lista los ingredientes separados por comas.")
    instrucciones = models.TextField()
    tiempo_preparacion = models.CharField(max_length=50, blank=True) 
    def __str__(self):
        return self.nombre