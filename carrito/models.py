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
    
    # --- CAMBIOS CLAVE AQUÍ ---
    total = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total final (Subtotal + Envío)")
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    metodo_envio_elegido = models.CharField(max_length=100, blank=True, null=True, default="Retiro")
    # --- FIN DE CAMBIOS ---
    
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='pendiente')
    direccion_envio = models.CharField(max_length=255, null=True, blank=True)
    ciudad_envio = models.CharField(max_length=100, null=True, blank=True)
    codigo_postal_envio = models.CharField(max_length=10, null=True, blank=True)
    telefono_contacto = models.CharField(max_length=20, null=True, blank=True)
    codigo_seguimiento = models.CharField(max_length=100, blank=True, null=True, help_text="Código de seguimiento manual")

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.username}"
    
    def get_subtotal(self):
        # El subtotal es el total menos el envío
        return self.total - self.costo_envio

    def get_costo_envio(self):
        # Simplemente devuelve el costo de envío guardado
        return self.costo_envio

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

    def get_costo(self):
        # Verificamos si los valores existen (no son None) antes de multiplicar
        if self.precio_unitario is not None and self.cantidad is not None:
            return self.precio_unitario * self.cantidad
        return 0