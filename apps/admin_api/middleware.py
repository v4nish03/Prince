from .auth import decode_jwt
from django.contrib.auth.models import AnonymousUser
from graphql import GraphQLError
import logging

logger = logging.getLogger(__name__)


def graphql_jwt_middleware(next, root, info, **args):
    request = info.context
    auth = request.META.get('HTTP_AUTHORIZATION', '')

    if auth.startswith('Bearer ') or auth.startswith('JWT '):
        token = auth.split(' ')[1]
        try:
            user = decode_jwt(token)
            request.user = user if user else AnonymousUser()
        except Exception:
            request.user = AnonymousUser()
    else:
        request.user = AnonymousUser()

    return next(root, info, **args)
