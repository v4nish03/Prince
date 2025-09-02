from functools import wraps
from graphql import GraphQLError

def validar_usuario_vendedor(func):
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Autenticación requerida.")
        if not user.is_seller:
            raise GraphQLError("Acceso denegado: Se requiere ser vendedor.")
        return func(root, info, *args, **kwargs)
    return wrapper