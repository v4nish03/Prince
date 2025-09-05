# apps/user_api/queries/queriesProductos.py
import graphene
from graphql import GraphQLError
from apps.common.models.producto import Producto
from apps.user_api.types import ProductoType
from apps.user_api.validador import validar_usuario_vendedor



class QueryProductos(graphene.ObjectType):
    mis_productos = graphene.List(ProductoType)
    producto_por_id = graphene.Field(ProductoType, producto_id=graphene.Int(required=True))
    productos_por_estado = graphene.List(ProductoType, estado=graphene.String(required=True))


    @validar_usuario_vendedor
    def resolve_mis_productos(self, info):
        tienda = info.context.user.tienda
        return Producto.objects.filter(tienda=tienda)

    @validar_usuario_vendedor
    def resolve_producto_por_id(self, info, producto_id):
        user = info.context.user
        try:    
            return Producto.objects.get(id=producto_id, tienda__propietario=user)
        except Producto.DoesNotExist:
            raise GraphQLError("Producto no encontrado o no pertenece a tu tienda.")

    @validar_usuario_vendedor
    def resolve_productos_por_estado(self, info, estado):
        tienda = info.context.user.tienda
        return Producto.objects.filter(tienda=tienda, estado=estado)
