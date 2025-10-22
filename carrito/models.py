from django.db import models
from django.contrib.auth.models import User
from productos.models import Producto

class Pedido(models.Model):
    ESTADOS_PEDIDO = (
        ('pendiente', 'Pendiente de Pago'),
        ('pagado', 'Pagado'),
        ('en_preparacion', 'En Preparación'),
        ('despachado', 'Despachado'),
        ('cancelado', 'Cancelado'),
    )

    cliente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='pendiente')
    
    direccion_envio = models.CharField(max_length=255, null=True, blank=True)
    ciudad_envio = models.CharField(max_length=100, null=True, blank=True)
    codigo_postal_envio = models.CharField(max_length=10, null=True, blank=True)
    telefono_contacto = models.CharField(max_length=20, null=True, blank=True)
    
    metodo_envio_elegido = models.CharField(max_length=100, blank=True, null=True, help_text="Método de envío que seleccionó el cliente (ej: Andreani)")
    codigo_seguimiento = models.CharField(max_length=100, blank=True, null=True, help_text="Código de seguimiento manual de Andreani/Correo")

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.username}"
    
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    # --- CORRECCIÓN CLAVE AQUÍ ---
    def get_costo(self):
        # Verificamos si los valores existen (no son None) antes de multiplicar
        if self.precio_unitario is not None and self.cantidad is not None:
            return self.precio_unitario * self.cantidad
        return 0 # Si son None, devolvemos 0

