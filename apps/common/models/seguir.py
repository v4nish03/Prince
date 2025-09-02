from django.db import models
from django.conf import settings
from apps.common.models import Tienda, CustomUser, Producto

class Seguimiento(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tiendas_seguidas')
    tienda = models.ForeignKey('common.Tienda', on_delete=models.CASCADE, related_name='seguidores')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'tienda')
        indexes = [
            models.Index(fields=['usuario']),
            models.Index(fields=['tienda']),
        ]
        ordering = ['-fecha_creacion']
        

    def __str__(self):
        return f"{self.usuario} sigue {self.tienda}"
  