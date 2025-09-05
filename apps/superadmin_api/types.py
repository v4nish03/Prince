import graphene
from apps.common.models.user import CustomUser
from graphene_django import DjangoObjectType

class UserType(DjangoObjectType):
    class Meta:
        model = CustomUser
        fields = ("id", "email", "username", "nombre", "apellidos","is_staff", "is_superuser")
        

