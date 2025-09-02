from django.db import models
from django.conf import settings

class Tienda(models.Model):
    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tiendas'
    )
    estados = (
        ('activo', 'Activo'),
        ('suspendida', 'Suspendida'),
        ('pendiente_eliminacion', 'Pendiente de Eliminación'),
        ('eliminada', 'Eliminada'),
    )
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True) 
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    creacion = models.DateTimeField(auto_now_add=True)
    actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=30, choices=estados, default='activo')
    fecha_eliminacion = models.DateTimeField(blank=True, null=True)
    foto_perfil = models.ImageField(upload_to='media/tiendas/logos/', blank=True, null=True)

    def __str__(self):
        return self.nombre
