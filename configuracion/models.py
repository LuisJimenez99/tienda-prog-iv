from django.db import models
from colorfield.fields import ColorField

class DatosPago(models.Model):
        cbu_alias = models.CharField(max_length=255, help_text="Tu CBU o Alias para transferencias.")
        link_mercado_pago = models.URLField(max_length=400, help_text="El enlace de pago de Mercado Pago.")

        def __str__(self):
            return "Datos de Pago"

        class Meta:
            verbose_name = "Datos de Pago"
    
    
class HeroSectionConfig(models.Model):
    # Campos para la imagen y el texto principal
    imagen_fondo = models.ImageField(upload_to='hero_images/', verbose_name="Imagen de Fondo", help_text="Imagen principal de la sección (se recomienda tamaño grande).")
    titulo_principal = models.CharField(max_length=200, verbose_name="Título Principal", help_text="Ej: Te ayudamos a lograr tus objetivos, sin perder el placer de comer.")
    descripcion = models.TextField(verbose_name="Descripción", help_text="Texto descriptivo debajo del título.")

    # Campos para el primer botón
    texto_boton_1 = models.CharField(max_length=50, verbose_name="Texto Botón 1", default="Viandas")
    url_boton_1 = models.URLField(max_length=200, verbose_name="URL Botón 1", default="/productos/")

    # Campos para el segundo botón
    texto_boton_2 = models.CharField(max_length=50, verbose_name="Texto Botón 2", default="Consultas")
    url_boton_2 = models.URLField(max_length=200, verbose_name="URL Botón 2", default="/turnos/")

    # Un campo para asegurarnos de que solo haya una configuración activa
    activa = models.BooleanField(default=True, verbose_name="¿Activa?", help_text="Marca esta opción para que esta configuración sea la visible.")

    class Meta:
        verbose_name = "Configuración de Sección Principal"
        verbose_name_plural = "Configuraciones de Sección Principal"

    def __str__(self):
        return f"Configuración Activa - {self.titulo_principal[:30]}..."

    # Opcional: Para asegurar que solo haya una activa
    def save(self, *args, **kwargs):
        if self.activa:
            # Desactiva cualquier otra configuración activa antes de guardar esta
            HeroSectionConfig.objects.filter(activa=True).exclude(pk=self.pk).update(activa=False)
        super().save(*args, **kwargs)
        
class CarruselImagen(models.Model):
    titulo = models.CharField(
        max_length=200, 
        blank=True, null=True, 
        verbose_name="Título (Opcional)", 
        help_text="Este texto aparecerá sobre la imagen."
    )
    imagen = models.ImageField(
        upload_to='carrusel/', 
        verbose_name="Imagen del carrusel",
        help_text="Sube la imagen para este slide."
    )
    link_url = models.URLField(
        max_length=300, 
        blank=True, null=True, 
        verbose_name="Enlace (Opcional)", 
        help_text="URL a la que dirigirá la imagen (ej: /productos/)"
    )
    abrir_en_nueva_pestana = models.BooleanField(
        default=False, 
        verbose_name="Abrir en nueva pestaña"
    )
    orden = models.PositiveIntegerField(
        default=0, 
        help_text="Define el orden de aparición (menor número primero)."
    )
    activo = models.BooleanField(
        default=True, 
        verbose_name="¿Mostrar esta imagen?",
        help_text="Desmarca esta casilla para ocultar esta imagen del carrusel."
    )

    class Meta:
        verbose_name = "Imagen de Carrusel"
        verbose_name_plural = "Imágenes de Carrusel"
        ordering = ['orden'] # Ordena las imágenes por el campo 'orden'

    def __str__(self):
        return self.titulo or f"Imagen de Carrusel {self.id}"


from django.db import models
from colorfield.fields import ColorField # <-- 1. Importa el ColorField

# ... (Aquí van tus otros modelos como HeroSectionConfig y DatosPago) ...

# --- MODELO NUEVO PARA APARIENCIA ---
class AparienciaConfig(models.Model):
    
    logo_sitio = models.ImageField(
        upload_to='logos/', 
        blank=True, null=True, 
        verbose_name="Logo del Sitio (Navbar)",
        help_text="Sube el logo que aparecerá en el menú. Si no subes ninguno, se mostrará el texto 'Mi Tienda'. Se ajustará a 50px de alto."
    )
    # --- Colores Globales (que ya teníamos) ---
    color_fondo_body = ColorField(
        default='#ECF0E5', 
        verbose_name="Color de Fondo Principal"
    )
    color_carrito_activo = ColorField(
        default='#E74C3C', # Un color rojo llamativo por defecto
        verbose_name="Color Contador Carrito (con items)",
        help_text="Color del círculo numérico del carrito cuando tiene productos."
    )
    # --- CAMPOS NUEVOS PARA EL NAVBAR ---
    navbar_color_fondo = ColorField(
        default='#FFFFFF',
        verbose_name="Color de Fondo (Navbar y Footer)"
    )
    navbar_color_enlaces = ColorField(
        default='#555555',
        verbose_name="Color de Texto (Enlaces del Nav)"
    )
    class EstilosTarjeta(models.TextChoices):
        SIMPLE = 'simple', 'Estilo Simple (Actual)'
        HOT_SALE = 'hot_sale', 'Estilo "Hot Sale" (Con insignia)'
        HARVEST = 'harvest', 'Estilo "Harvest" (Vase)'
        
    estilo_tarjeta_producto = models.CharField(
        max_length=20,
        choices=EstilosTarjeta.choices,
        default=EstilosTarjeta.SIMPLE,
        verbose_name="Estilo de Tarjetas de Producto",
        help_text="Elige el diseño que se usará para mostrar los productos en el catálogo."
    )
    class FuentesTarjeta(models.TextChoices):
        DEFAULT = '"Poppins", sans-serif', 'Fuente Principal (Poppins)'
        SERIF = '"Lora", serif', 'Fuente Elegante (Lora)'
        MODERNA = '"Segoe UI", sans-serif', 'Fuente Moderna (Segoe UI)'
        
    fuente_tarjetas = models.CharField(
        max_length=50,
        choices=FuentesTarjeta.choices,
        default=FuentesTarjeta.DEFAULT,
        verbose_name="Tipografía de Tarjetas"
    )

    # --- ¡NUEVO! Control de Color de Texto ---
    color_titulo_tarjeta = ColorField(
        default='#18181B', 
        verbose_name="Color Título (Tarjetas)"
    )
    color_desc_tarjeta = ColorField(
        default='#52525B', 
        verbose_name="Color Descripción (Tarjetas)"
    )
    

    # --- CAMPOS NUEVOS PARA BOTONES ---
    # (Los usaremos para TODOS los botones, incluidos los del Nav y Tarjetas)
    boton_color_principal_fondo = ColorField(
        default='#78857A', 
        verbose_name="Color Principal (Botones)"
    )
    boton_color_principal_texto = ColorField(
        default='#FFFFFF', 
        verbose_name="Color de Texto (Botones)"
    )
    boton_color_principal_hover = ColorField(
        default='#647066', 
        verbose_name="Color Hover (Botones)"
    )
    
    boton_color_secundario_borde = ColorField(
        default='#78857A',
        verbose_name="Color Secundario (Borde y Texto)"
    )
    card_btn_principal_fondo = ColorField(
        default='#78857A', 
        verbose_name="[Tarjeta] Color Principal (Fondo)"
    )
    card_btn_principal_texto = ColorField(
        default='#FFFFFF', 
        verbose_name="[Tarjeta] Color Principal (Texto)"
    )
    card_btn_principal_hover = ColorField(
        default='#647066', 
        verbose_name="[Tarjeta] Color Principal (Hover)"
    )
    card_btn_secundario_borde = ColorField(
        default='#78857A',
        verbose_name="[Tarjeta] Color Secundario (Borde)"
    )
    # ... (podríamos añadir más, pero empecemos con estos) ...

    class Meta:
        verbose_name = "Configuración de Apariencia"
        verbose_name_plural = "Configuración de Apariencia"

    def __str__(self):
        return "Configuración de Apariencia"
