from django.db import models
from django.contrib.auth import get_user_model

customUser = get_user_model()

class UserLog(models.Model):
    ORIGENES = [
        ('web', 'Web'),
        ('api_externa', 'API Externa'),
        ('mobile', 'Móvil'),
    ]

    RESULTADOS = [
        ('exito', 'Éxito'),
        ('fallo', 'Fallo'),
        ('casi', 'Casi'),
    ]

    usuario = models.ForeignKey(customUser, on_delete=models.CASCADE, null=True, blank=True, related_name='logs')
    fechaHora = models.DateTimeField(auto_now_add=True)

    tipoAccion = models.CharField(max_length=100)
    rutaAcceso = models.CharField(max_length=255)
    origenConexion = models.CharField(max_length=100, choices=ORIGENES)

    direccionIP = models.GenericIPAddressField(blank=True, null=True)
    dispositivo = models.CharField(max_length=100, blank=True, null=True)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)  # opcional
    resultado = models.CharField(max_length=20, choices=RESULTADOS, blank=True, null=True)
    
    detalles = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.usuario} - {self.tipoAccion} - {self.fechaHora.strftime('%Y-%m-%d %H:%M:%S')}"
