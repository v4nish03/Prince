# apps/user_api/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.common.models.producto import Producto  # ajusta import si tu ruta cambia
from apps.common.models.seguir import Seguimiento
from apps.common.models.notificacion import Notificacion

@receiver(post_save, sender=Producto)
def notificar_seguidores_nuevo_producto(sender, instance, created, **kwargs):
    if not created:
        return

    tienda = getattr(instance, 'tienda', None)
    if tienda is None:
        return

    # Traer IDs de usuarios que siguen esa tienda
    seguidores_ids = list(
        Seguimiento.objects.filter(tienda=tienda)
        .values_list('usuario_id', flat=True)
    )

    if not seguidores_ids:
        return

    mensaje = f"¡{tienda.nombre} publicó un nuevo producto: {getattr(instance, 'nombre', str(instance))}!"

    notifs = [
        Notificacion(
            usuario_id=uid,
            tienda=tienda,
            producto=instance,
            tipo='nuevo_producto',
            mensaje=mensaje
        )
        for uid in seguidores_ids
    ]
    Notificacion.objects.bulk_create(notifs)
