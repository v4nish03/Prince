import graphene
from graphene_django.types import DjangoObjectType
from apps.common.models.producto import Producto
from apps.common.models.categoria import Categoria
from apps.common.models.tienda import Tienda
from apps.common.models.favoritos import Favorito
from apps.common.models.seguir import Seguimiento   
from apps.common.models.notificacion import Notificacion
from apps.common.models import CustomUser as Usuario
from apps.common.models.imagen import Imagen
from apps.common.models.seguir import Seguimiento

class ProductoType(DjangoObjectType):
    url = graphene.String()
    class Meta:
        model = Producto
        fields = "__all__"
        
    def resolve_url(self, info):
        if not self.tienda.id: #Verifica que el producto tenga una tienda asociada
            return None
        request = info.context
        if info.context is not None:
            return request.build_absolute_uri(f"/tienda/{self.tienda.id}/producto/{self.id}")
        else:
            return f"/tienda/{self.tienda.id}/producto/{self.id}"

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
        
class PerfilType(DjangoObjectType):
    class Meta:
        model = Usuario
        fields = ("id", "email", "username", "nombre", "apellidos", "celular", "is_seller", "password")
        
class ImagenType(DjangoObjectType):
    url = graphene.String()
    
    class Meta:
        model = Imagen
        fields = "__all__"
        
    def resolve_url(self, info):
        """Resolver para obtener la URL absoluta del archivo"""
        if self.archivo and hasattr(self.archivo, 'url'):
            request = info.context
            if request is not None:
                return request.build_absolute_uri(self.archivo.url)
            else:
                return self.archivo.url
        return None

class SeguimientoType(DjangoObjectType):
    class Meta:
        model = Seguimiento
        fields = "__all__"