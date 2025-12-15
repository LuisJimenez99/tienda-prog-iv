from django.db import models
from colorfield.fields import ColorField
from imagekit.models import ProcessedImageField # <-- 1. Importar
from imagekit.processors import ResizeToFit, Transpose
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

class DatosPago(models.Model):
    cbu_alias = models.CharField(max_length=255, help_text="Tu CBU o Alias para transferencias.")
    link_mercado_pago = models.URLField(max_length=400, help_text="El enlace de pago de Mercado Pago.")
    def __str__(self):
        return "Datos de Pago"
    class Meta:
        verbose_name = "Datos de Pago"

class HeroSectionConfig(models.Model):
    # Campo de imagen corregido:
    imagen_fondo = ProcessedImageField(
        upload_to='hero_images/',
        processors=[Transpose(), ResizeToFit(width=1920)], # Hero más grande (máx 1920px)
        format='WEBP',
        options={'quality': 80}, # Puede ser más agresivo
        blank=True, null=True, verbose_name="Imagen de Fondo"
    )
    titulo_principal = models.CharField(max_length=200, verbose_name="Título Principal", help_text="Ej: Te ayudamos a lograr tus objetivos, sin perder el placer de comer.")
    descripcion = models.TextField(verbose_name="Descripción", help_text="Texto descriptivo debajo del título.")
    texto_boton_1 = models.CharField(max_length=50, verbose_name="Texto Botón 1", default="Viandas")
    url_boton_1 = models.URLField(max_length=200, verbose_name="URL Botón 1", default="/productos/")
    texto_boton_2 = models.CharField(max_length=50, verbose_name="Texto Botón 2", default="Consultas")
    url_boton_2 = models.URLField(max_length=200, verbose_name="URL Botón 2", default="/turnos/")
    activa = models.BooleanField(default=True, verbose_name="¿Activa?", help_text="Marca esta opción para que esta configuración sea la visible.")
    class Meta:
        verbose_name = "Configuración de Sección Principal"
        verbose_name_plural = "Configuraciones de Sección Principal"
    def __str__(self):
        return f"Configuración Activa - {self.titulo_principal[:30]}..."
    def save(self, *args, **kwargs):
        if self.activa:
            HeroSectionConfig.objects.filter(activa=True).exclude(pk=self.pk).update(activa=False)
        super().save(*args, **kwargs)

class CarruselImagen(models.Model):
    titulo = models.CharField(max_length=200, blank=True, null=True, verbose_name="Título (Opcional)", help_text="Este texto aparecerá sobre la imagen.")
    
    # Campo de imagen corregido:
    imagen = ProcessedImageField(
        upload_to='carrusel/',
        processors=[Transpose(), ResizeToFit(width=1200)], # Carrusel (máx 1200px)
        format='WEBP',
        options={'quality': 85},
        blank=True, null=True, verbose_name="Imagen del carrusel"
    )
    
    link_url = models.URLField(max_length=300, blank=True, null=True, verbose_name="Enlace (Opcional)", help_text="URL a la que dirigirá la imagen (ej: /productos/)")
    abrir_en_nueva_pestana = models.BooleanField(default=False, verbose_name="Abrir en nueva pestaña")
    orden = models.PositiveIntegerField(default=0, help_text="Define el orden de aparición (menor número primero).")
    activo = models.BooleanField(default=True, verbose_name="¿Mostrar esta imagen?", help_text="Desmarca esta casilla para ocultar esta imagen del carrusel.")
    class Meta:
        verbose_name = "Imagen de Carrusel"
        verbose_name_plural = "Imágenes de Carrusel"
        ordering = ['orden']
    def __str__(self):
        return self.titulo or f"Imagen de Carrusel {self.id}"

class AparienciaConfig(models.Model):
    
    # Campo de imagen corregido:
    logo_sitio = ProcessedImageField(
        upload_to='logos/',
        processors=[Transpose(), ResizeToFit(height=80)], # Redimensionar por altura (máx 80px de alto)
        format='PNG', # Conservar PNG para logos transparentes
        options={'quality': 90},
        blank=True, null=True, verbose_name="Logo del Sitio (Navbar)"
    )
   
    color_fondo_body = ColorField(default='#ECF0E5', verbose_name="Color de Fondo Principal")
    color_carrito_activo = ColorField(default='#E74C3C', verbose_name="Color Contador Carrito (con items)", help_text="Color del círculo numérico del carrito cuando tiene productos.")
    navbar_color_fondo = ColorField(default='#FFFFFF', verbose_name="Color de Fondo (Navbar y Footer)")
    navbar_color_enlaces = ColorField(default='#555555', verbose_name="Color de Texto (Enlaces del Nav)")
    
    class EstilosTarjeta(models.TextChoices):
        SIMPLE = 'simple', 'Estilo Simple (Actual)'
        HOT_SALE = 'hot_sale', 'Estilo "Hot Sale" (Con insignia)'
        HARVEST = 'harvest', 'Estilo "Harvest" (Vase)'
    estilo_tarjeta_producto = models.CharField(max_length=20, choices=EstilosTarjeta.choices, default=EstilosTarjeta.SIMPLE, verbose_name="Estilo de Tarjetas de Producto", help_text="Elige el diseño que se usará para mostrar los productos en el catálogo.")
    
    class FuentesTarjeta(models.TextChoices):
        DEFAULT = '"Poppins", sans-serif', 'Fuente Principal (Poppins)'
        SERIF = '"Lora", serif', 'Fuente Elegante (Lora)'
        MODERNA = '"Segoe UI", sans-serif', 'Fuente Moderna (Segoe UI)'
    fuente_tarjetas = models.CharField(max_length=50, choices=FuentesTarjeta.choices, default=FuentesTarjeta.DEFAULT, verbose_name="Tipografía de Tarjetas")
    
    color_titulo_tarjeta = ColorField(default='#18181B', verbose_name="Color Título (Tarjetas)")
    color_desc_tarjeta = ColorField(default='#52525B', verbose_name="Color Descripción (Tarjetas)")
    boton_color_principal_fondo = ColorField(default='#78857A', verbose_name="Color Principal (Botones)")
    boton_color_principal_texto = ColorField(default='#FFFFFF', verbose_name="Color de Texto (Botones)")
    boton_color_principal_hover = ColorField(default='#647066', verbose_name="Color Hover (Botones)")
    boton_color_secundario_borde = ColorField(default='#78857A', verbose_name="Color Secundario (Borde y Texto)")
    card_btn_principal_fondo = ColorField(default='#78857A', verbose_name="[Tarjeta] Color Principal (Fondo)")
    card_btn_principal_texto = ColorField(default='#FFFFFF', verbose_name="[Tarjeta] Color Principal (Texto)")
    card_btn_principal_hover = ColorField(default='#647066', verbose_name="[Tarjeta] Color Principal (Hover)")
    card_btn_secundario_borde = ColorField(default='#78857A', verbose_name="[Tarjeta] Color Secundario (Borde)")
    
    footer_col_contacto_titulo = models.CharField(max_length=50, default="Contacto", verbose_name="Título Columna Contacto")
    footer_col_contacto_texto = models.TextField(max_length=200, default="¿Tienes una consulta? <br> ¡Escríbeme!", verbose_name="Texto Columna Contacto", blank=True)
    footer_link_instagram = models.URLField(max_length=255, blank=True, null=True, verbose_name="Enlace Instagram", help_text="URL completa (ej: https://instagram.com/...)")
    footer_link_whatsapp = models.URLField(max_length=255, blank=True, null=True, verbose_name="Enlace WhatsApp", help_text="URL completa (ej: https://wa.me/123456...)")
    footer_texto_creditos = models.CharField(max_length=100, default="Luis Jiménez", verbose_name="Nombre Creador (Footer)")
    
    class Meta:
        verbose_name = "Configuración de Apariencia"
        verbose_name_plural = "Configuración de Apariencia"
    def __str__(self):
        return "Configuración de Apariencia"

class Servicio(models.Model):
    # ... (El modelo Servicio queda igual) ...
    TIPO_SERVICIO_CHOICES = [
        ('TURNO', 'Consulta (Enlaza al Calendario de Turnos)'),
        ('RECETARIO', 'Recetario (Genera un Pago Directo)'),
    ]
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Servicio")
    descripcion = models.TextField(verbose_name="Descripción Corta", help_text="Un párrafo corto explicando el servicio.")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (ej: 25000.00)")
    tipo_servicio = models.CharField(max_length=10, choices=TIPO_SERVICIO_CHOICES, default='TURNO', verbose_name="Tipo de Botón", help_text="Esto define qué hace el botón 'Contratar': enlazar al calendario o generar un pago.")
    icono = models.CharField(max_length=50, blank=True, null=True, verbose_name="Icono (Clase de Font Awesome)", help_text="Opcional. Ej: 'fas fa-calendar-alt' o 'fas fa-book-open'")
    orden = models.PositiveIntegerField(default=0, help_text="Define el orden de aparición (menor número primero).")
    activo = models.BooleanField(default=True, verbose_name="¿Mostrar este servicio en la página?")
    class Meta:
        verbose_name = "Servicio / Plan"
        verbose_name_plural = "Servicios / Planes"
        ordering = ['orden']
    def __str__(self):
        return self.nombre


class EmailConfig(models.Model):
    TIPOS_EMAIL = (
        ('TRANSFERENCIA', 'Instrucciones de Transferencia'),
        ('DESPACHADO', 'Pedido Despachado (Envío)'),
        ('PAGO_CONFIRMADO', 'Pago Confirmado (Recibo)'),
    )

    tipo = models.CharField(max_length=50, choices=TIPOS_EMAIL, unique=True, verbose_name="Tipo de Email")
    asunto = models.CharField(max_length=200, help_text="Puedes usar variables como {{ pedido.id }}")
    
    contenido = models.TextField(
        verbose_name="Cuerpo del Email (HTML)", 
        help_text="""
        Escribe aquí el contenido. Puedes usar HTML simple (<b>negrita</b>, <br> saltos).
        <br><strong>Variables Disponibles:</strong>
        <ul>
            <li>{{ pedido.id }} - ID del pedido</li>
            <li>{{ pedido.total }} - Total a pagar</li>
            <li>{{ cliente.first_name }} - Nombre del cliente</li>
            <li>{{ datos_pago.cbu_alias }} - Alias/CBU</li>
            <li>{{ codigo_seguimiento }} - (Solo para envíos)</li>
        </ul>
        """
    )

    class Meta:
        verbose_name = "Configuración de Email"
        verbose_name_plural = "Configuraciones de Email"

    def __str__(self):
        return self.get_tipo_display()


class ConfigPrecio(models.Model):
    """
    Modelo único (Singleton) para guardar precios globales.
    """
    precio_consulta = models.DecimalField(
        max_digits=10, decimal_places=2, 
        default=1500.00, 
        verbose_name="Precio de Consulta (Turno)"
    )
    
    precio_recetario_mensual = models.DecimalField(
        max_digits=10, decimal_places=2, 
        default=3000.00, 
        verbose_name="Precio Recetario (Mensual)"
    )
    
    # Podemos agregar más precios aquí en el futuro (ej: planes trimestrales)

    def __str__(self):
        return "Configuración de Precios"

    class Meta:
        verbose_name = "Configuración de Precios"
        verbose_name_plural = "Configuración de Precios"

    # Método para asegurar que solo haya uno
    def save(self, *args, **kwargs):
        if not self.pk and ConfigPrecio.objects.exists():
            # Si ya existe uno, actualizamos el primero en lugar de crear otro
            return ConfigPrecio.objects.first()
        return super(ConfigPrecio, self).save(*args, **kwargs)