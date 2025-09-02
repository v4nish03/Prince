import graphene
from graphene_django import DjangoObjectType
from ..models import SuperAdmin
from ..utils.jwt_superadmin import generate_jwt
from ..decorador import superadmin_required

class SuperAdminType(DjangoObjectType):
    class Meta:
        model = SuperAdmin
        fields = ("id", "username", "email")
        
class CrearSuperAdmin(graphene.Mutation):
    superadmin = graphene.Field(SuperAdminType)
    ok = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, username, email, password):
        # Verifica si ya existe un SuperAdministrador (solo debería haber uno en todo el sistema)
        if SuperAdmin.objects.exists():
            return CrearSuperAdmin(ok=False, message="Ya existe un SuperAdmin registrado")

        superadmin = SuperAdmin(username=username, email=email)
        superadmin.set_password(password)
        superadmin.save()
        return CrearSuperAdmin(superadmin=superadmin, ok=True, message="SuperAdmin creado correctamente")

class LoginSuperAdmin(graphene.Mutation):
    token = graphene.String()
    ok = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
    @superadmin_required
    def mutate(self, info, email, password):
        try:
            superadmin = SuperAdmin.objects.get(email=email)
        except SuperAdmin.DoesNotExist:
            return LoginSuperAdmin(ok=False, message="SuperAdmin no encontrado")

        if not superadmin.check_password(password):
            return LoginSuperAdmin(ok=False, message="Contraseña incorrecta")

        # Generar JWT
        token = generate_jwt(superadmin)

        return LoginSuperAdmin(ok=True, token=token, message="Login exitoso")


class Mutation(graphene.ObjectType):
    crear_superadmin = CrearSuperAdmin.Field()
    login_superadmin = LoginSuperAdmin.Field()