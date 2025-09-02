import apps.superadmin_api.utils.jwt_superadmin as jwt_superadmin
from django.conf import settings
from datetime import datetime, timezone, timedelta
from ..models import SuperAdmin

JWT_SECRET = getattr(settings, 'SECRET_KEY', 'superadmin_secret')
JWT_ALGORITMO = 'HS256'
JWT_EXP = timedelta(hours=8)


def generate_jwt(superadmin:SuperAdmin):
    payload = {
        'superadmin_id': superadmin.id,
        'username': superadmin.username,
        'exp': datetime.now(tz=timezone.utc) + JWT_EXP,
        'iat': datetime.now(tz=timezone.utc)
    }
    token = jwt_superadmin.encode(payload, JWT_SECRET, algoritmo=JWT_ALGORITMO)
    return token

def verificar_jwt(token: str):
    try:
        payload = jwt_superadmin.decode(token, JWT_SECRET, algoritmo=[JWT_ALGORITMO])
        superadmin = SuperAdmin.objects.get(id=payload['superadmin_id'])
        return superadmin
    except (jwt_superadmin.ExpiredSignatureError, jwt_superadmin.DecodeError, SuperAdmin.DoesNotExist):
        return None