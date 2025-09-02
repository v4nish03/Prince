from django.db import models
from django.conf import settings
from apps.common.models import Tienda, CustomUser, Producto
# Create your models here.
class Notificacion(models.Model):
    opciones = ('nuevo_producto', 'Nuevo producto'), ('general',  'General')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificaciones')
    tienda = models.ForeignKey('common.Tienda', on_delete=models.CASCADE, null=True, blank=True)
    
    tipo = models.CharField(max_length=50, choices=opciones, default='general')
    mensaje = models.TextField()
    
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    producto = models.ForeignKey('common.Producto', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['usuario', 'leida']),
            models.Index(fields=['fecha_creacion']),
        ]
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Notificación {self.usuario}"  