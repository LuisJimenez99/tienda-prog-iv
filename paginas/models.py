from django.db import models
from imagekit.models import ProcessedImageField # <-- 1. Importar
from imagekit.processors import ResizeToFit, Transpose

class Pagina(models.Model):
    titulo = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, help_text="Versión del título amigable para URLs (ej: sobre-mi)")
    
   
    imagen_principal = ProcessedImageField(
        upload_to='paginas/',
        processors=[Transpose(), ResizeToFit(width=1024)], # (máx 1024px)
        format='WEBP',
        options={'quality': 85},
        null=True, blank=True,
        help_text="La foto principal que aparecerá en la página."
    )
    subtitulo = models.CharField(
        max_length=255, 
        null=True, blank=True, 
        help_text="Una frase corta que aparece debajo del título principal."
    )
    contenido_principal = models.TextField(
        null=True, blank=True, 
        help_text="El párrafo de introducción o biografía principal."
    )
    seccion_extra_titulo = models.CharField(
        max_length=200, 
        null=True, blank=True, 
        help_text="Título para la sección secundaria (ej: Mi Filosofía)."
    )
    seccion_extra_contenido = models.TextField(
        null=True, blank=True, 
        help_text="Contenido para la sección secundaria."
    )

    def __str__(self):
        return self.titulo


