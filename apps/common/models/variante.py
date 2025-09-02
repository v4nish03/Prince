from django.db import models
from apps.common.models.producto import Producto
from apps.common.models.talla import Talla

class Variante(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='variantes')
    talla = models.ForeignKey(Talla, on_delete=models.SET_NULL, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    
    class Meta:
        unique_together = ('producto', 'talla', 'color')
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.talla or "Sin talla"} - {self.color or "Sin color"}"