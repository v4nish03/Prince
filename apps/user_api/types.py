import graphene
from graphene_django.types import DjangoObjectType
from apps.common.models.producto import Producto
from apps.common.models.categoria import Categoria
from apps.common.models.tienda import Tienda
from apps.common.models.favoritos import Favorito
from apps.common.models.seguir import Seguimiento   
from apps.common.models.notificacion import Notificacion
class ProductoType(DjangoObjectType):
    class Meta:
        model = Producto
        fields = "__all__"

class CategoriaType(DjangoObjectType):
    class Meta:
        model = Categoria
        fields = "__all__"

class TiendaType(DjangoObjectType):
    class Meta:
        model = Tienda
        fields = "__all__"

class FavoritoType(DjangoObjectType):
    class Meta:
        model = Favorito
        fields = "__all__"
        
class SeguimientoType(DjangoObjectType):
    class Meta:
        model = Seguimiento
        fields = ("id", "usuario", "tienda", "fecha_creacion")
        
class NotificacionType(DjangoObjectType):
    class Meta:
        model = Notificacion
        fields = ("id", "usuario", "tienda", "producto", "tipo", "mensaje", "leida", "fecha_creacion")