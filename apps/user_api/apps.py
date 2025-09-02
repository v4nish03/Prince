from django.apps import AppConfig


class UserApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.user_api'

    def ready(self):
        import apps.common.models.signal