from graphene_file_upload.django import FileUploadGraphQLView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from apps.user_api.auth import decode_jwt
from django.contrib.auth.models import AnonymousUser

@method_decorator(csrf_exempt, name='dispatch')
class UserFileUploadGraphQLView(FileUploadGraphQLView):
    def dispatch(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        token = None

        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        elif auth_header.startswith('JWT '):
            token = auth_header.split(' ')[1]

        if token:
            user = decode_jwt(token)
            request.user = user if user is not None else AnonymousUser()
        else:
            request.user = AnonymousUser()

        return super().dispatch(request, *args, **kwargs)

    def get_context(self, request):
        return request
