from django.db import models
from apps.common.models.tienda import Tienda
from apps.common.models.categoria import Categoria
from apps.common.models.talla import Talla

class Producto(models.Model):
    estados = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('agotado', 'Agotado'),
    )
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='productos')
    categoria = models.ManyToManyField(Categoria, related_name='productos', blank=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    precioBase = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=estados, default='activo')
    fechaCreacion = models.DateTimeField(auto_now_add=True)
    fechaActualizacion = models.DateTimeField(auto_now=True)
    talla = models.ForeignKey(Talla, on_delete=models.SET_NULL, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.nombre