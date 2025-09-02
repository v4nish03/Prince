import graphene
from graphene_django import DjangoObjectType
from apps.superadmin_api.models import SuperAdmin
from datetime import datetime, timezone
import jwt
from django.conf import settings    

class SuperAdminType(DjangoObjectType):
    class Meta:
        model = SuperAdmin
        fields = ("id", "username", "email")
        
class Query(graphene.ObjectType):
    superadmins = graphene.List(SuperAdminType)

    def resolve_superadmins(root, info):
        return SuperAdmin.objects.all()