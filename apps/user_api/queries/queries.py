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

# Decorador para proteger queries que requieren autenticación
def login_required(func):
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Autenticación requerida")
        return func(root, info, *args, **kwargs)
    return wrapper

# Decorador para proteger queries que requieren ser vendedor
def vendedor_required(func):
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Autenticación requerida.")
        if not user.is_seller:
            raise GraphQLError("Permiso denegado. Solo vendedores pueden realizar esta acción.")
        if not Tienda.objects.filter(propietario=user, estado="activo").exists():
            raise GraphQLError("Debes tener una tienda activa para crear productos.")
        return func(root, info, *args, **kwargs)
    return wrapper


# Clase principal de Queries
class Query(QueryProductos,graphene.ObjectType):
    # --------- QUERIES PÚBLICAS ---------
    categorias = graphene.List(CategoriaType)
    productos = graphene.List(ProductoType)
    buscar_productos = graphene.List(ProductoType, nombre=graphene.String(required=True))
    productos = graphene.List(ProductoType, limit=graphene.Int(), offset=graphene.Int())
    productos_por_categoria = graphene.List(ProductoType, categoria_id=graphene.Int(required=True))
    productos_por_tipo = graphene.List(ProductoType, tipo=graphene.String(required=True))
    tiendas = graphene.List(TiendaType)
    tienda_por_id = graphene.Field(TiendaType, tienda_id=graphene.Int(required=True))

    def resolve_categorias(self, info):
        return Categoria.objects.filter()
    
    def resolve_producto(self, info):
        from apps.common.models.producto import Producto
        return Producto.objects.get(id=id)

    def resolve_productos(self, info, limit=None, offset=None):
        queryset = Producto.objects.select_related('tienda', 'categoria').prefetch_related('imagenes').all()
        if offset is not None:
            queryset = queryset[offset:]
        elif limit is not None:
            queryset = queryset[:limit]
        return queryset

    def resolve_buscar_productos(self, info, nombre):
        return Producto.objects.select_related('tienda', 'categoria').prefetch_related('imagenes').filter(nombre__icontains=nombre, estado='activo')

    def resolve_productos_por_categoria(self, info, categoria_id):
        return Producto.objects.select_related('tienda', 'categoria').prefetch_related('imagenes').filter(categoria_id=categoria_id, estado='activo')

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
    perfil = graphene.Field(PerfilType)
    mis_favoritos = graphene.List(ProductoType)
    mis_tiendas_seguidas = graphene.List(TiendaType)
    mis_seguimientos = graphene.List(SeguimientoType)
    mis_notificaciones = graphene.List(
        NotificacionType,
        solo_no_leidas=graphene.Boolean(required=False, default_value=False)
    )

    @login_required
    def resolve_perfil(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("No autenticado")
        return user
    
    @login_required
    def resolve_mis_favoritos(self, info):
        user = info.context.user
        return [fav.producto for fav in Favorito.objects.select_related('producto').filter(usuario=user)]

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
    mis_tiendas = graphene.List(TiendaType)
    mis_productos = graphene.List(ProductoType, tienda_id=graphene.Int(required=True))
    
    @login_required
    @vendedor_required
    def resolve_mis_tiendas(self, info):
        user = info.context.user
        return Tienda.objects.filter(propietario=user, estado='activo')
    
    @login_required
    @vendedor_required
    def resolve_tienda_perfil(self, info, tienda_id):
        user = info.context.user
        try:
            tienda = Tienda.objects.get(id=tienda_id, propietario=user, estado="activo")
            return tienda
        except Tienda.DoesNotExist:
            return None
        
    @login_required
    @vendedor_required
    def resolve_mis_productos(self, info, tienda_id):
        return Producto.objects.filter(tienda_id=tienda_id)