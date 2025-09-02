from django.db import models
from django.conf import settings
from apps.common.models.producto import Producto

class Favorito(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favoritos'
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, related_name='favorited_by' 
    )
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('usuario', 'producto')
        verbose_name = "Favorito"
        verbose_name_plural = "Favoritos"
        ordering = ['-fecha']   
        
    def __str__(self):
        return f"{self.usuario} - {self.producto}"
    

    