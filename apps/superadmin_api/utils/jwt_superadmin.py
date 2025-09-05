import jwt
from django.conf import settings
from datetime import datetime, timezone, timedelta
from ..models import SuperAdmin

JWT_SECRET = getattr(settings, 'SECRET_KEY', 'superadmin_secret')
JWT_ALGORITMO = 'HS256'
JWT_EXP = timedelta(hours=8)


def generate_jwt(superadmin: SuperAdmin):
    payload = {
        'superadmin_id': superadmin.id,
        'username': superadmin.username,
        'exp': datetime.now(tz=timezone.utc) + JWT_EXP,
        'iat': datetime.now(tz=timezone.utc)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITMO)
    return token


def verificar_jwt(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITMO])
        superadmin = SuperAdmin.objects.get(id=payload['superadmin_id'])
        return superadmin
    except (jwt.ExpiredSignatureError, jwt.DecodeError, SuperAdmin.DoesNotExist):
        return None
