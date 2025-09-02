import jwt
from django.conf import settings
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

def generate_jwt(user):
    payload = {
        'user_id': user.id,
        'email': user.email,        
        'username': user.username,  
        'is_admin': getattr(user, "is_admin_user", user.is_staff or user.is_superuser), 
        'is_seller': user.is_seller,    
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token if isinstance(token, str) else token.decode()

def decode_jwt(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload['user_id'])
        return user
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return None


