from graphql import GraphQLError
from functools import wraps

def superadmin_required(fn):
    @wraps(fn)
    def wrapper(self, info, *args, **kwargs):
        request = info.context
        sa = getattr(request, 'superadmin', None)
        if not sa:
            raise GraphQLError("No autorizado, se requiere SuperAdmin valido")
        return fn(self, info, *args, **kwargs)
    return wrapper