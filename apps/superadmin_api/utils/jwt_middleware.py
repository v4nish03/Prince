# apps/superadmin_api/middleware/jwt_superadmin_middleware.py
from apps.superadmin_api.utils.jwt_superadmin import verificar_jwt
from django.contrib.auth.models import AnonymousUser

class SuperAdminJWTMiddleware:
    def resolve(self, next, root, info, **kwargs):
        request = info.context
        request.user = AnonymousUser()
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            superadmin = verificar_jwt(token)
            if superadmin:
                request.user = superadmin
        return next(root, info, **kwargs)
