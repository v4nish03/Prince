from functools import wraps
from graphql import GraphQLError

def admin_required(func):
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        user = info.context.user
        if not user or user.is_anonymous:
            raise GraphQLError("La autenticación es requerida")
        if not (user.is_staff or user.is_superuser):
            raise GraphQLError("Permisos insuficientes: Se requiere usuario administrador")
        return func(root, info, *args, **kwargs)
    return wrapper
