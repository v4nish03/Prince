from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    icono = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    categoriaPadre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='subcategorias',
        blank=True,
        null=True
    )
    
    def __str__(self):
        return self.nombre