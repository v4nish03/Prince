import logging
import jwt
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
#from .auth import decode_jwt
from apps.superadmin_api.models import SuperAdmin
from apps.superadmin_api.utils.jwt_superadmin import verificar_jwt


logger = logging.getLogger(__name__)

class SuperAdminJWTMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.superadmin = None
        auth_header = request.headers.get("Authorization") if hasattr(request, 'headers') else None
        if not auth_header:
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header:
            return None
        
        token = None
        auth = auth_header.strip()
        if auth.startswith("Bearer "):
            token = auth.split(" ", 1)[1].strip()
        elif auth.startswith("JWT "):
            token = auth.split(" ", 1)[1].strip()
        else:
            token = auth
        if not token:
            return None
        
        if verificar_jwt:
            try:
                sa = verificar_jwt(token)
                if sa:
                    request.superadmin = sa
                    return None
            except Exception as e:
                logger.debug(f"Error verificando token: {e}")
                
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            superadmin_id = payload.get("superadmin_id") or payload.get("id") or payload.get("superadminid") or payload.get("sub_id")
            if not superadmin_id and payload.get("sub") in ("superadmin", "super-admin"):
                superadmin_id = payload.get("id") or payload.get("superadmin_id")

            if superadmin_id:
                try:
                    request.superadmin = SuperAdmin.objects.get(id=superadmin_id)
                except SuperAdmin.DoesNotExist:
                    request.superadmin = None
            else:
                request.superadmin = None

        except jwt.ExpiredSignatureError:
            logger.debug("JWT expirado")
            request.superadmin = None
        except jwt.InvalidTokenError:
            logger.debug("JWT inválido")
            request.superadmin = None
        except Exception as exc:
            logger.exception(f"Error validando JWT SuperAdmin: {exc}")
            request.superadmin = None

        return None