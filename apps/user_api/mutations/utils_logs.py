import inspect
import asyncio
from apps.common.models.log import UserLog

def log_mutation(func):
    if inspect.iscoroutinefunction(func):
        # Para funciones async
        async def async_wrapper(root, info, **kwargs):
            user = info.context.user
            user_agent = info.context.META.get("HTTP_USER_AGENT", "").lower()
            origen = "mobile" if "mobile" in user_agent else "web"
            ip = info.context.META.get("REMOTE_ADDR")
            action = info.field_name.upper()
            try:
                result = await func(root, info, **kwargs)
                UserLog.objects.create(
                    usuario=user if user.is_authenticated else None,
                    tipoAccion=action,
                    rutaAcceso="/graphql",
                    origenConexion=origen,
                    direccionIP=ip,
                    resultado="exito",
                    detalles={"args": kwargs},
                )
                return result
            except Exception as e:
                UserLog.objects.create(
                    usuario=user if user.is_authenticated else None,
                    tipoAccion=action,
                    rutaAcceso="/graphql",
                    origenConexion=origen,
                    direccionIP=ip,
                    resultado="fallo",
                    detalles={"args": kwargs, "error": str(e)},
                )
                raise e
        return async_wrapper
    else:
        # Para funciones sync
        def sync_wrapper(root, info, **kwargs):
            user = info.context.user
            user_agent = info.context.META.get("HTTP_USER_AGENT", "").lower()
            origen = "mobile" if "mobile" in user_agent else "web"
            ip = info.context.META.get("REMOTE_ADDR")
            action = info.field_name.upper()
            try:
                result = func(root, info, **kwargs)
                UserLog.objects.create(
                    usuario=user if user.is_authenticated else None,
                    tipoAccion=action,
                    rutaAcceso="/graphql",
                    origenConexion=origen,
                    direccionIP=ip,
                    resultado="exito",
                    detalles={"args": kwargs},
                )
                return result
            except Exception as e:
                UserLog.objects.create(
                    usuario=user if user.is_authenticated else None,
                    tipoAccion=action,
                    rutaAcceso="/graphql",
                    origenConexion=origen,
                    direccionIP=ip,
                    resultado="fallo",
                    detalles={"args": kwargs, "error": str(e)},
                )
                raise e
        return sync_wrapper
