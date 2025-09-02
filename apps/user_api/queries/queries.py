import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from apps.common.models import CustomUser, Categoria, Producto, Tienda, Imagen
from apps.common.models.favoritos import Favorito
from functools import wraps
from .queriesProductos import QueryProductos
from apps.common.models import Seguimiento, Notificacion
from apps.user_api.types import SeguimientoType, NotificacionType
from apps.user_api.types import PerfilType,CategoriaType, ProductoType, TiendaType, ImagenType, SeguimientoType 

# class PerfilType(graphene.ObjectType):
#     email = graphene.String()
#     username = graphene.String()
#     nombre = graphene.String()
#     apellidos = graphene.String()
#     celular = graphene.String()
#     is_seller = graphene.Boolean()
#     password = graphene.String()


# # Tipos de datos para GraphQL
# class CategoriaType(graphene.ObjectType):
#     id = graphene.Int()
#     nombre = graphene.String()


# class ProductoType(graphene.ObjectType):
#     id = graphene.Int()
#     nombre = graphene.String()
#     descripcion = graphene.String()
#     precio = graphene.Float()
#     tipo = graphene.String()
#     categoria = graphene.Field(CategoriaType)
#     tienda_id = graphene.Int()
#     url = graphene.String()

#     def resolve_url(self, info):
#         request = info.context
#         return request.build_absolute_uri(f"/tienda/{self.tienda_id}/producto/{self.id}")


# class TiendaType(graphene.ObjectType):
#     id = graphene.Int()
#     nombre = graphene.String()
#     descripcion = graphene.String()
#     telefono = graphene.String()
#     direccion = graphene.String()
#     estado = graphene.String()
#     foto_perfil = graphene.String()
#     propietario_id = graphene.Int()
#     url = graphene.String() 

#     def resolve_url(self, info):
#         request = info.context
#         return request.build_absolute_uri(f"/tienda/{self.id}")
    
#     def resolve_propietario_id(self, info):
#         return self.propietario.id

# class ImagenType(graphene.ObjectType):
#     url = graphene.String()

#     class Meta:
#         model = Imagen
#         fields = ('id', 'nombre', 'archivo', 'esPrincipal', 'orden', 'producto', 'variante')

#     def resolve_url(self, info):
#         if self.archivo and hasattr(self.archivo, 'url'):
#             request = info.context
#             if request is not None:
#                 return request.build_absolute_uri(self.archivo.url)
#             else:
#                 return self.archivo.url
#         return None
    
# class SeguimientoType(DjangoObjectType):
#     class Meta:
#         model = Seguimiento
#         fields = ("id", "usuario", "tienda", "fecha_creacion")
        
# class NotificacionType(DjangoObjectType):
#     class Meta:
#         model = Notificacion
#         fields = ("id", "usuario", "tienda", "producto", "tipo", "mensaje", "leida", "fecha_creacion")

# Decorador para proteger queries que requieren autenticación
def login_required(func):
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Autenticación requerida")
        return func(root, info, *args, **kwargs)
    return wrapper




# Clase principal de Queries
class Query(QueryProductos,graphene.ObjectType):
    # --------- QUERIES PÚBLICAS ---------
    categorias = graphene.List(CategoriaType)
    productos = graphene.List(ProductoType)
    buscar_productos = graphene.List(ProductoType, nombre=graphene.String(required=True))
    productos_por_categoria = graphene.List(ProductoType, categoria_id=graphene.Int(required=True))
    productos_por_tipo = graphene.List(ProductoType, tipo=graphene.String(required=True))
    tiendas = graphene.List(TiendaType)
    tienda_por_id = graphene.Field(TiendaType, tienda_id=graphene.Int(required=True))
    perfil = graphene.Field(PerfilType)
    
    
    mis_tiendas_seguidas = graphene.List(TiendaType)
    mis_seguimientos = graphene.List(SeguimientoType)
    mis_notificaciones = graphene.List(
        NotificacionType,
        solo_no_leidas=graphene.Boolean(required=False, default_value=False)
    )

    def resolve_categorias(self, info):
        return Categoria.objects.filter()
    
    def resolve_producto(self, info):
        from apps.common.models.producto import Producto
        return Producto.objects.get(id=id)

    def resolve_productos(self, info):
        from apps.common.models.producto import Producto
        return Producto.objects.all()

    def resolve_buscar_productos(self, info, nombre):
        return Producto.objects.filter(nombre__icontains=nombre, estado='activo')

    def resolve_productos_por_categoria(self, info, categoria_id):
        return Producto.objects.filter(categoria_id=categoria_id, estado='activo')

    def resolve_productos_por_tipo(self, info, tipo):
        return Producto.objects.filter(tipo__iexact=tipo, estado='activo')

    def resolve_tiendas(self, info):
        from apps.common.models.tienda import Tienda
        return Tienda.objects.all()

    def resolve_tienda_por_id(self, info, tienda_id):
        from apps.common.models.tienda import Tienda
        try:
            return Tienda.objects.get(id=tienda_id)
        except Tienda.DoesNotExist:
            raise GraphQLError("Tienda no encontrada")

    # --------- QUERIES PRIVADAS (con login) ---------
    mis_favoritos = graphene.List(ProductoType)
    mis_tiendas = graphene.List(TiendaType)

    @login_required
    def resolve_perfil(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("No autenticado")
        return user
    
    @login_required
    def resolve_mis_favoritos(self, info):
        user = info.context.user
        return [fav.producto for fav in Favorito.objects.filter(usuario=user)]

    @login_required
    def resolve_mis_tiendas_seguidas(self, info):
        user = info.context.user
        segs = Seguimiento.objects.select_related('tienda').filter(usuario=user)
        return [s.tienda for s in segs]
    
    @login_required
    def resolve_mis_seguimientos(self, info):
        user = info.context.user
        return Seguimiento.objects.filter(usuario=user)
    
    @login_required
    def resolve_mis_notificaciones(self, info, solo_no_leidas=False):
        user = info.context.user
        qs = Notificacion.objects.filter(usuario=user)
        if solo_no_leidas:
            qs = qs.filter(leida=False)
        return qs.order_by('-fecha_creacion')
    
    
    #QUERIES PRIVADAS DE VENDEDORES
    tienda_perfil = graphene.Field(TiendaType, tienda_id=graphene.Int(required=True))
    @login_required
    def resolve_mis_tiendas(self, info):
        user = info.context.user
        return Tienda.objects.filter(propietario=user, estado='activo')
    
    @login_required
    def resolve_tienda_perfil(self, info, tienda_id):
        try:
            tienda = Tienda.objects.get(id=tienda_id, estado="activo")
            return tienda
        except Tienda.DoesNotExist:
            return None