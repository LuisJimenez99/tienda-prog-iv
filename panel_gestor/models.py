from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Paciente(models.Model):
    # Relación opcional con el usuario web (OneToOne)
    # Si se borra el usuario web, el paciente queda (on_delete=models.SET_NULL)
    usuario = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='ficha_paciente'
    )
    
    # Datos personales (Independientes del usuario web)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True, verbose_name="Email de contacto")
    telefono = models.CharField(max_length=20, blank=True, null=True)
    
    # Datos clínicos básicos
    fecha_nacimiento = models.DateField(blank=True, null=True)
    observaciones = models.TextField(
        blank=True, 
        null=True, 
        help_text="Alergias, objetivos, notas clínicas..."
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['-fecha_creacion']




class Consulta(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='consultas')
    fecha = models.DateField(default=timezone.now)
    
    # --- DATOS BÁSICOS ---
    peso_actual = models.DecimalField(max_digits=5, decimal_places=2, help_text="En Kg")
    altura = models.DecimalField(max_digits=4, decimal_places=2, help_text="En Metros (ej: 1.75)")
    
    # --- CHECKBOX ACTIVADOR ---
    realizo_antropometria = models.BooleanField(default=False, verbose_name="¿Se realizó Antropometría ISAK?")
    
    # --- ANTROPOMETRÍA (Opcionales, solo si el checkbox es True) ---
    # Composición Corporal (Resultados finales)
    porcentaje_grasa = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="% Grasa")
    porcentaje_musculo = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="% Músculo")
    
    # Medidas Clave (Para seguimiento)
    cintura = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Cintura (cm)")
    cadera = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Cadera (cm)")
    
    # Sumatoria de pliegues (Indicador rápido)
    sumatoria_pliegues = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Sumatoria 6 Pliegues (mm)")

    notas_evolucion = models.TextField(blank=True, null=True, verbose_name="Notas de la Consulta")

    class Meta:
        ordering = ['-fecha'] # Las más nuevas primero

    def __str__(self):
        return f"Consulta {self.fecha} - {self.paciente}"
    
    @property
    def imc(self):
        """Calcula el Índice de Masa Corporal automáticamente"""
        if self.altura > 0:
            return round(float(self.peso_actual) / (float(self.altura) ** 2), 2)
        return 0

class ArchivoPaciente(models.Model):
    """
    Estudios médicos, fotos o documentos adjuntos.
    """
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='archivos')
    archivo = models.FileField(upload_to='pacientes_archivos/')
    titulo = models.CharField(max_length=100, verbose_name="Nombre del Archivo")
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} ({self.paciente})"

    def es_imagen(self):
        name = self.archivo.name.lower()
        return name.endswith('.jpg') or name.endswith('.png') or name.endswith('.jpeg') or name.endswith('.webp')

class PlanAlimentacion(models.Model):
    """
    La dieta o pauta alimentaria actual del paciente.
    """
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='planes')
    contenido = models.TextField(help_text="Escribe aquí el plan detallado.")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Plan {self.fecha_creacion.strftime('%d/%m/%Y')} - {self.paciente}"