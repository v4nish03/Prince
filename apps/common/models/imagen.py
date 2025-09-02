from django.db import models
from apps.common.models.producto import Producto
from apps.common.models.variante import Variante

class Imagen(models.Model):
    nombre = models.CharField(max_length=255, blank=True, null=True)
    archivo = models.ImageField(upload_to='media/imagenesProductos/')
    esPrincipal = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=0)
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes', blank=True, null=True)
    variante = models.ForeignKey(Variante, on_delete=models.CASCADE, related_name='imagenes', blank=True, null=True)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.producto and not self.variante:
            raise ValidationError("Debe asociar la imagen a un producto o una variante.")
        if self.producto and self.variante:
            raise ValidationError("No puede asociar una imagen a un producto y una variante al mismo tiempo.")
        
    def __str__(self):
        return self.nombre or f"Imagen #{self.id}"