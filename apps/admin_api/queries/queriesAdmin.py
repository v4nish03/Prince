import graphene
from graphql import GraphQLError
from apps.common.models import CustomUser, Tienda, Categoria, Producto, Variante, Imagen
from apps.common.models.log import UserLog
from graphene_django.types import DjangoObjectType
from ..validador import admin_required  

# Definición de tipos GraphQL
class UserType(DjangoObjectType):
    class Meta:
        model = CustomUser
        fields = "__all__"

class TiendaType(DjangoObjectType):
    class Meta:
        model = Tienda
        fields = "__all__"

class CategoriaType(DjangoObjectType):
    class Meta:
        model = Categoria
        fields = "__all__"

class ProductoType(DjangoObjectType):
    class Meta:
        model = Producto
        fields = "__all__"

class VarianteType(DjangoObjectType):
    class Meta:
        model = Variante
        fields = "__all__"

class ImagenType(DjangoObjectType):
    class Meta:
        model = Imagen
        fields = "__all__"

class LogType(DjangoObjectType):
    class Meta:
        model = UserLog
        fields = "__all__"
    
    usuario_id = graphene.Int()
    usuario_username = graphene.String()

    def resolve_usuario_id(self, info):
        return self.usuario.id if self.usuario else None

    def resolve_usuario_username(self, info):
        return self.usuario.username if self.usuario else None

class Query(graphene.ObjectType):

    all_users = graphene.List(UserType, limit=graphene.Int(), offset=graphene.Int())
    all_tiendas = graphene.List(TiendaType, limit=graphene.Int(), offset=graphene.Int())
    all_categorias = graphene.List(CategoriaType, limit=graphene.Int(), offset=graphene.Int())
    all_productos = graphene.List(ProductoType, limit=graphene.Int(), offset=graphene.Int())
    all_variantes = graphene.List(VarianteType, limit=graphene.Int(), offset=graphene.Int())
    all_imagenes = graphene.List(ImagenType, limit=graphene.Int(), offset=graphene.Int())
    all_logs = graphene.List(LogType, limit=graphene.Int(), offset=graphene.Int(), tipo_accion=graphene.String(), usuario_id=graphene.ID())

    # Buscar por ID
    user_by_id = graphene.Field(UserType, id=graphene.ID(required=True))
    tienda_by_id = graphene.Field(TiendaType, id=graphene.ID(required=True))
    categoria_by_id = graphene.Field(CategoriaType, id=graphene.ID(required=True))
    producto_by_id = graphene.Field(ProductoType, id=graphene.ID(required=True))
    variante_by_id = graphene.Field(VarianteType, id=graphene.ID(required=True))
    imagen_by_id = graphene.Field(ImagenType, id=graphene.ID(required=True))
    log_by_id = graphene.Field(LogType, id=graphene.ID(required=True))


    # Usuarios
    @admin_required
    def resolve_all_users(self, info, limit=None, offset=None):
        qs = CustomUser.objects.all().order_by('id')
        if offset:
            qs = qs[offset:]
        if limit:
            qs = qs[:limit]
        return qs

    @admin_required
    def resolve_user_by_id(self, info, id):
        try:
            return CustomUser.objects.get(pk=id)
        except CustomUser.DoesNotExist:
            raise GraphQLError("Usuario no encontrado")

    # Tiendas
    @admin_required
    def resolve_all_tiendas(self, info, limit=None, offset=None):
        qs = Tienda.objects.all().order_by('id')
        if offset:
            qs = qs[offset:]
        if limit:
            qs = qs[:limit]
        return qs

    @admin_required
    def resolve_tienda_by_id(self, info, id):
        try:
            return Tienda.objects.get(pk=id)
        except Tienda.DoesNotExist:
            raise GraphQLError("Tienda no encontrada")

    # Categorías
    @admin_required
    def resolve_all_categorias(self, info, limit=None, offset=None):
        qs = Categoria.objects.all().order_by('id')
        if offset:
            qs = qs[offset:]
        if limit:
            qs = qs[:limit]
        return qs

    @admin_required
    def resolve_categoria_by_id(self, info, id):
        try:
            return Categoria.objects.get(pk=id)
        except Categoria.DoesNotExist:
            raise GraphQLError("Categoría no encontrada")

    # Productos
    @admin_required
    def resolve_all_productos(self, info, limit=None, offset=None):
        qs = Producto.objects.all().order_by('id')
        if offset:
            qs = qs[offset:]
        if limit:
            qs = qs[:limit]
        return qs

    @admin_required
    def resolve_producto_by_id(self, info, id):
        try:
            return Producto.objects.get(pk=id)
        except Producto.DoesNotExist:
            raise GraphQLError("Producto no encontrado")

    # Variantes
    @admin_required
    def resolve_all_variantes(self, info, limit=None, offset=None):
        qs = Variante.objects.all().order_by('id')
        if offset:
            qs = qs[offset:]
        if limit:
            qs = qs[:limit]
        return qs

    @admin_required
    def resolve_variante_by_id(self, info, id):
        try:
            return Variante.objects.get(pk=id)
        except Variante.DoesNotExist:
            raise GraphQLError("Variante no encontrada")

    # Imágenes
    @admin_required
    def resolve_all_imagenes(self, info, limit=None, offset=None):
        qs = Imagen.objects.all().order_by('id')
        if offset:
            qs = qs[offset:]
        if limit:
            qs = qs[:limit]
        return qs

    @admin_required
    def resolve_imagen_by_id(self, info, id):
        try:
            return Imagen.objects.get(pk=id)
        except Imagen.DoesNotExist:
            raise GraphQLError("Imagen no encontrada")

    # Logs
    @admin_required
    def resolve_all_logs(self, info, limit=None, offset=None, tipo_accion=None, usuario_id=None):
        qs = UserLog.objects.all().order_by('-fechaHora')
        if tipo_accion:
            qs = qs.filter(tipoAccion=tipo_accion)
        if usuario_id:
            qs = qs.filter(usuario__id=usuario_id)
        if offset:
            qs = qs[offset:]
        if limit:
            qs = qs[:limit]
        return qs

    @admin_required
    def resolve_log_by_id(self, info, id):
        try:
            return UserLog.objects.get(pk=id)
        except UserLog.DoesNotExist:
            raise GraphQLError("Log no encontrado")
