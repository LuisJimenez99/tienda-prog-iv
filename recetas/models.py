from django.db import models

class Receta(models.Model):
    nombre = models.CharField(max_length=150)
    imagen = models.ImageField(upload_to='recetas/')
    ingredientes = models.TextField(help_text="Lista los ingredientes separados por comas.")
    instrucciones = models.TextField()
    tiempo_preparacion = models.CharField(max_length=50, blank=True) 

    def __str__(self):
        return self.nombre
