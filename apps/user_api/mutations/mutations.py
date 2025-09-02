import graphene
from graphql import GraphQLError
from .utils_logs import log_mutation
from apps.common.models import (CustomUser,Tienda,Categoria,Producto,Variante,Imagen,
                                Talla,
                                UserLog,)
from apps.common.models.favoritos import Favorito
from apps.user_api.types import SeguimientoType, Seguimiento, Notificacion, NotificacionType
from ..auth import generate_jwt
from django.contrib.auth import authenticate
from functools import wraps
from ..validador import validar_usuario_vendedor
from django.core.files.base import ContentFile
from graphene_file_upload.scalars import Upload
import uuid

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

def login_required(func):
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Autenticación requerida")
        return func(root, info, *args, **kwargs)
    return wrapper

# ===== MUTACIONES DE USUARIO EXISTENTES =====

class LoginUsuario(graphene.Mutation):
    token = graphene.String()
    user_id = graphene.Int()
    email = graphene.String()
    username = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, email, password):
        user_agent = info.context.META.get("HTTP_USER_AGENT", "").lower()
        origen = "mobile" if "mobile" in user_agent else "web"
        ip = info.context.META.get("REMOTE_ADDR")

        user = authenticate(username=email, password=password)

        if not user:
            # Registrar intento fallido
            UserLog.objects.create(
                usuario=None,
                tipoAccion="LOGIN",
                rutaAcceso="/graphql/user/login",  # o la ruta exacta de tu endpoint
                origenConexion=origen,
                direccionIP=ip,
                resultado="fallo",
                detalles={"email_intento": email}
            )
            raise GraphQLError("Correo o contraseña incorrectos.")

        # Registrar login exitoso
        UserLog.objects.create(
            usuario=user,
            tipoAccion="LOGIN",
            rutaAcceso="/graphql/user/login",
            origenConexion=origen,
            direccionIP=ip,
            resultado="exito",
            detalles={"email": user.email}
        )

        token = generate_jwt(user)
        return LoginUsuario(
            token=token, user_id=user.id, email=user.email, username=user.username
        )
class RegistroUsuario(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    user_id = graphene.Int()

    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        nombre = graphene.String(required=True)
        apellidos = graphene.String(required=True)
        celular = graphene.String()

    @log_mutation
    def mutate(self, info, username, email, password, nombre, apellidos, celular=None):
        if CustomUser.objects.filter(email=email).exists():
            raise GraphQLError("Ya existe un usuario con este email.")
        if CustomUser.objects.filter(username=username).exists():
            raise GraphQLError("Nombre de usuario en uso.")

        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            username=username,
            nombre=nombre,
            apellidos=apellidos,
            celular=celular,
            is_staff=False,
            is_superuser=False,
            is_seller=False,
        )
        return RegistroUsuario(
            ok=True, message="Usuario creado correctamente.", user_id=user.id
        )

class EditarPerfil(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        nombre = graphene.String()
        apellidos = graphene.String()
        celular = graphene.String()
        foto_perfil = Upload()

    @login_required
    @log_mutation
    def mutate(self, info, nombre=None, apellidos=None, celular=None, foto_perfil=None):
        user = info.context.user
        if nombre:
            user.nombre = nombre
        if apellidos:
            user.apellidos = apellidos
        if celular:
            user.celular = celular
            
        # Correcion para cambiar imagen de perfil
        if foto_perfil:
            user.foto_perfil = foto_perfil
        user.save()
        return EditarPerfil(ok=True, message="Perfil actualizado correctamente.")

class CambiarContrasena(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        old_password = graphene.String(required=True)
        new_password = graphene.String(required=True)

    @login_required
    @log_mutation
    def mutate(self, info, old_password, new_password):
        user = info.context.user
        if not user.check_password(old_password):
            raise GraphQLError("Contraseña actual incorrecta.")
        user.set_password(new_password)
        user.save()
        return CambiarContrasena(ok=True, message="Contraseña cambiada correctamente.")

class ActivarVendedor(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    
    class Arguments:
        pass
    @login_required
    def mutate(self, info):
        user = info.context.user
        
        if user.is_seller:
            return ActivarVendedor(ok=True, message="Ya eres vendedor.")

        user.is_seller = True
        user.save()
        
        return ActivarVendedor(ok=True, message="Ahora eres vendedor.")
# ===== NUEVAS MUTACIONES DE TIENDA =====

class CrearTienda(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    tienda_id = graphene.Int()

    class Arguments:
        nombre = graphene.String(required=True)
        descripcion = graphene.String()
        direccion = graphene.String()
        telefono = graphene.String()
        foto_perfil = Upload()

    @login_required
    def mutate(self, info, nombre, descripcion=None, direccion=None, telefono=None, foto_perfil=None):
        user = info.context.user
        
        # Limita al usuario a tener 5 tiendas activas
        if Tienda.objects.filter(propietario=user, estado='activo').count() >= 5:
            raise GraphQLError("Se alcanzo el limite de 5 tiendas por usuario.")
        
        # Crear la tienda
        tienda = Tienda.objects.create(
            propietario=user,
            nombre=nombre,
            descripcion=descripcion,
            direccion=direccion,
            telefono=telefono,
            estado='activo',
            foto_perfil=foto_perfil,
        )
        
        # Convertir al usuario en vendedor si no lo es
        if not user.is_seller:
            user.is_seller = True
            user.save()
        
        return CrearTienda(
            ok=True, 
            message="Tienda creada correctamente.", 
            tienda_id=tienda.id
        )

class EditarTienda(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        nombre = graphene.String()
        descripcion = graphene.String()
        direccion = graphene.String()
        telefono = graphene.String()

    @vendedor_required
    def mutate(self, info, nombre=None, descripcion=None, direccion=None, telefono=None):
        user = info.context.user
        tienda = Tienda.objects.get(propietario=user, estado="activo")
        
        if nombre:
            tienda.nombre = nombre
        if descripcion:
            tienda.descripcion = descripcion
        if direccion:
            tienda.direccion = direccion
        if telefono:
            tienda.telefono = telefono
        
        tienda.save()
        return EditarTienda(ok=True, message="Tienda actualizada correctamente.")

class EliminarTienda(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        tienda_id = graphene.ID(required=True)

    @vendedor_required
    def mutate(self, info, tienda_id):
        user = info.context.user
        try:
            tienda = Tienda.objects.get(id=tienda_id, propietario=user, estado="activo")
            # Soft delete - marcar como inactiva
            tienda.estado = 'eliminada'
            tienda.save()
            return EliminarTienda(ok=True, message="Tienda desactivada correctamente.")
        except Tienda.DoesNotExist:
            return EliminarTienda(ok=False, message="Tienda no encontrada.")
        

# ===== MUTACIONES DE PRODUCTO MEJORADAS =====

class CrearProducto(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    producto_id = graphene.Int()

    class Arguments:
        nombre = graphene.String(required=True)
        descripcion = graphene.String()
        precioBase = graphene.Float(required=True)
        categoria_id = graphene.Int(required=True)
        tienda_id = graphene.Int(required=True)
        
    @vendedor_required
    def mutate(self, info, nombre, descripcion, precioBase, categoria_id, tienda_id):
        user = info.context.user
        validar_usuario_vendedor(user)

        try:
            categoria = Categoria.objects.get(id=categoria_id)
        except Categoria.DoesNotExist:
            raise GraphQLError("Categoría no encontrada")

        try:
            tienda = Tienda.objects.get(id=tienda_id,propietario=user, estado='activo')
        except Tienda.DoesNotExist:
            raise GraphQLError("El vendedor no tiene una tienda activa")
        
        producto = Producto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precioBase=precioBase,
            categoria=categoria,
            tienda=tienda,
            estado='activo'
        )
        
        # Notificar a los seguidores de la subida de productos de la tienda
        seguidores = Seguimiento.objects.filter(tienda=tienda)
        for seguidor in seguidores:
            Notificacion.objects.create(
                usuario=seguidor.usuario,
                tienda=tienda,
                producto=producto,
                tipo='nuevo_producto',
                mensaje=f"{tienda.nombre} ha añadido un nuevo producto: {producto.nombre}",
            )

        return CrearProducto(ok=True, message="Producto creado correctamente", producto_id=producto.id)

class EditarProducto(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        producto_id = graphene.Int(required=True)
        nombre = graphene.String()
        descripcion = graphene.String()
        precio_base = graphene.Float()
        categoria_id = graphene.Int()
        estado = graphene.String()

    @vendedor_required
    def mutate(self, info, producto_id, nombre=None, descripcion=None, precio_base=None, categoria_id=None, estado=None):
        user = info.context.user
        tienda = Tienda.objects.get(propietario=user, estado="activo")

        try:
            producto = Producto.objects.get(id=producto_id, tienda=tienda)
        except Producto.DoesNotExist:
            raise GraphQLError("Producto no encontrado.")

        if nombre:
            producto.nombre = nombre
        if descripcion:
            producto.descripcion = descripcion
        if precio_base:
            producto.precioBase = precio_base
        if categoria_id:
            try:
                categoria = Categoria.objects.get(id=categoria_id)
                producto.categoria = categoria
            except Categoria.DoesNotExist:
                raise GraphQLError("Categoría no válida.")
        if estado in ['activo', 'inactivo', 'agotado']:
            producto.estado = estado

        producto.save()
        return EditarProducto(ok=True, message="Producto actualizado correctamente.")

class EliminarProducto(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        producto_id = graphene.Int(required=True)

    @vendedor_required
    def mutate(self, info, producto_id):
        user = info.context.user
        tienda = Tienda.objects.get(propietario=user, estado="activo")

        try:
            producto = Producto.objects.get(id=producto_id, tienda=tienda)
        except Producto.DoesNotExist:
            raise GraphQLError("Producto no encontrado.")

        producto.estado = 'inactivo'
        producto.save()
        return EliminarProducto(ok=True, message="Producto eliminado (soft delete).")

# ===== NUEVAS MUTACIONES DE VARIANTES =====

class CrearVariante(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    variante_id = graphene.Int()

    class Arguments:
        producto_id = graphene.Int(required=True)
        talla_id = graphene.Int()
        color = graphene.String()
        precio = graphene.Float(required=True)
        stock = graphene.Int(required=True)

    @vendedor_required
    def mutate(self, info, producto_id, precio, stock, talla_id=None, color=None):
        user = info.context.user
        tienda = Tienda.objects.get(propietario=user, estado="activo")

        try:
            producto = Producto.objects.get(id=producto_id, tienda=tienda)
        except Producto.DoesNotExist:
            raise GraphQLError("Producto no encontrado.")

        talla = None
        if talla_id:
            try:
                talla = Talla.objects.get(id=talla_id)
            except Talla.DoesNotExist:
                raise GraphQLError("Talla no encontrada.")

        # Verificar que no exista ya esta combinación
        if Variante.objects.filter(producto=producto, talla=talla, color=color).exists():
            raise GraphQLError("Ya existe una variante con esta combinación de talla y color.")

        variante = Variante.objects.create(
            producto=producto,
            talla=talla,
            color=color,
            precio=precio,
            stock=stock
        )

        return CrearVariante(
            ok=True, 
            message="Variante creada correctamente.", 
            variante_id=variante.id
        )

class EditarVariante(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        variante_id = graphene.Int(required=True)
        talla_id = graphene.Int()
        color = graphene.String()
        precio = graphene.Float()
        stock = graphene.Int()

    @vendedor_required
    def mutate(self, info, variante_id, talla_id=None, color=None, precio=None, stock=None):
        user = info.context.user
        tienda = Tienda.objects.get(propiertario=user, estado="activo")

        try:
            variante = Variante.objects.get(id=variante_id, producto__tienda=tienda)
        except Variante.DoesNotExist:
            raise GraphQLError("Variante no encontrada.")

        if talla_id:
            try:
                talla = Talla.objects.get(id=talla_id)
                variante.talla = talla
            except Talla.DoesNotExist:
                raise GraphQLError("Talla no encontrada.")
        
        if color is not None:
            variante.color = color
        if precio is not None:
            variante.precio = precio
        if stock is not None:
            variante.stock = stock

        variante.save()
        return EditarVariante(ok=True, message="Variante actualizada correctamente.")

class EliminarVariante(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        variante_id = graphene.Int(required=True)

    @vendedor_required
    def mutate(self, info, variante_id):
        user = info.context.user
        tienda = Tienda.objects.get(propietario=user, estado="activo")

        try:
            variante = Variante.objects.get(id=variante_id, producto__tienda=tienda)
        except Variante.DoesNotExist:
            raise GraphQLError("Variante no encontrada.")

        variante.delete()
        return EliminarVariante(ok=True, message="Variante eliminada correctamente.")

# ===== NUEVAS MUTACIONES DE IMÁGENES =====

class SubirImagenProducto(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    imagen_id = graphene.Int()

    class Arguments:
        producto_id = graphene.Int(required=True)
        archivo = Upload(required=True)
        nombre = graphene.String()
        es_principal = graphene.Boolean()
        orden = graphene.Int()

    @vendedor_required
    def mutate(self, info, producto_id, archivo, nombre=None, es_principal=False, orden=0):
        user = info.context.user
        try:
            tienda = Tienda.objects.get(propietario=user, estado='activo')
        except Tienda.DoesNotExist:
            raise GraphQLError("No tienes una tienda activa.")

        try:
            producto = Producto.objects.get(id=producto_id, tienda=tienda)
        except Producto.DoesNotExist:
            raise GraphQLError("Producto no encontrado.")

        if es_principal:
            Imagen.objects.filter(producto=producto, esPrincipal=True).update(esPrincipal=False)

        imagen = Imagen.objects.create(
            producto=producto,
            archivo=archivo, 
            nombre=nombre or f"Imagen de {producto.nombre}",
            esPrincipal=es_principal,
            orden=orden
        )

        return SubirImagenProducto(
            ok=True, 
            message="Imagen subida correctamente.", 
            imagen_id=imagen.id
        )

class SubirImagenVariante(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    imagen_id = graphene.Int()

    class Arguments:
        variante_id = graphene.Int(required=True)
        imagen_base64 = graphene.String(required=True)
        nombre = graphene.String()
        es_principal = graphene.Boolean()
        orden = graphene.Int()

    @vendedor_required
    def mutate(self, info, variante_id, imagen_base64, nombre=None, es_principal=False, orden=0):
        user = info.context.user
        tienda = Tienda.objects.get(propietario=user, estado="activo")

        try:
            variante = Variante.objects.get(id=variante_id, producto__tienda=tienda)
        except Variante.DoesNotExist:
            raise GraphQLError("Variante no encontrada.")

        try:
            # Decodificar imagen base64
            format, imgstr = imagen_base64.split(';base64,')
            ext = format.split('/')[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            data = ContentFile(base64.b64decode(imgstr), name=filename)
            
            # Si es principal, quitar el flag de las demás imágenes de la variante
            if es_principal:
                Imagen.objects.filter(variante=variante, esPrincipal=True).update(esPrincipal=False)

            imagen = Imagen.objects.create(
                variante=variante,
                archivo=data,
                nombre=nombre or f"Imagen de {variante}",
                esPrincipal=es_principal,
                orden=orden
            )

            return SubirImagenVariante(
                ok=True, 
                message="Imagen subida correctamente.", 
                imagen_id=imagen.id
            )

        except Exception as e:
            raise GraphQLError(f"Error al procesar la imagen: {str(e)}")

class EliminarImagen(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        imagen_id = graphene.Int(required=True)

    @vendedor_required
    def mutate(self, info, imagen_id):
        user = info.context.user
        try:
            tienda = Tienda.objects.get(propietario=user, estado="activo")
        except Tienda.DoesNotExist:
            raise GraphQLError("Tienda no encontrada o inactiva.")
        
        try:
            # Buscar imagen tanto en productos como en variantes de la tienda
            imagen = Imagen.objects.filter(
                id=imagen_id
            ).filter(
                models.Q(producto__tienda=tienda) | models.Q(variante__producto__tienda=tienda)
            ).first()
            
            if not imagen:
                raise GraphQLError("Imagen no encontrada.")
            
            # Eliminar archivo físico
            if imagen.archivo:
                imagen.archivo.delete()
            
            imagen.delete()
            return EliminarImagen(ok=True, message="Imagen eliminada correctamente.")

        except Exception as e:
            raise GraphQLError(f"Error al eliminar la imagen: {str(e)}")

class ActualizarOrdenImagen(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        imagen_id = graphene.Int(required=True)
        nuevo_orden = graphene.Int(required=True)

    @vendedor_required
    def mutate(self, info, imagen_id, nuevo_orden):
        user = info.context.user
        tienda = Tienda.objects.get(propietario=user, estado="activo")

        try:
            imagen = Imagen.objects.filter(
                id=imagen_id
            ).filter(
                models.Q(producto__tienda=tienda) | models.Q(variante__producto__tienda=tienda)
            ).first()
            
            if not imagen:
                raise GraphQLError("Imagen no encontrada.")
            
            imagen.orden = nuevo_orden
            imagen.save()
            
            return ActualizarOrdenImagen(ok=True, message="Orden de imagen actualizado correctamente.")

        except Exception as e:
            raise GraphQLError(f"Error al actualizar el orden: {str(e)}")
        
# ===== NUEVAS MUTACIONES DE FAVORITOS =====

class AgregarFavorito(graphene.Mutation):
    favorito = graphene.Field('apps.user_api.types.FavoritoType')
    
    class Arguments:
        producto_id = graphene.Int(required=True)
        
    def mutate(self, info, producto_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Autenticación requerida.")
        
        try:
            producto = Producto.objects.get(id=producto_id)
        except Producto.DoesNotExist:
            raise GraphQLError("Producto no encontrado.")
        
        favorito, created = Favorito.objects.get_or_create(usuario=user, producto=producto)
        
        if not created:
            raise GraphQLError("El producto ya está en tus favoritos.")
        return AgregarFavorito(favorito=favorito)
    
class EliminarFavorito(graphene.Mutation):
    ok = graphene.Boolean()
    
    class Arguments:
        producto_id = graphene.Int(required=True)
    
    def mutate(self, info, producto_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Autenticación requerida.")
        
        try:
            favorito = Favorito.objects.get(usuario=user, producto_id=producto_id)
            favorito.delete()
        except Favorito.DoesNotExist:
            raise GraphQLError("El producto no está en tus favoritos.")

# ===== NUEVAS MUTACIONES DE SEGUIR TIENDAS ====
class SeguirTienda(graphene.Mutation):
    class Arguments:
        tienda_id = graphene.ID(required=True)

    ok = graphene.Boolean()
    seguimiento = graphene.Field(SeguimientoType)

    @login_required
    def mutate(self, info, tienda_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("No autenticado")

        try:
            tienda = Tienda.objects.get(id=tienda_id)
        except Tienda.DoesNotExist:
            raise Exception("La tienda no existe")

        seguimiento, _ = Seguimiento.objects.get_or_create(usuario=user, tienda=tienda)
        return SeguirTienda(ok=True, seguimiento=seguimiento)

class DejarDeSeguirTienda(graphene.Mutation):
    class Arguments:
        tienda_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, tienda_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("No autenticado")

        try:
            seguimiento = Seguimiento.objects.get(usuario=user, tienda_id=tienda_id)
            seguimiento.delete()
            return DejarDeSeguirTienda(ok=True)
        except Seguimiento.DoesNotExist:
            raise Exception("No sigues esta tienda")

# ===== NUEVAS MUTACIONES DE NOTIFICACIONES ====
class MarcarNotificacionLeida(graphene.Mutation):
    class Arguments:
        notificacion_id = graphene.ID(required=True)

    ok = graphene.Boolean()
    notificacion = graphene.Field(NotificacionType)

    @login_required
    def mutate(self, info, notificacion_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("No autenticado")

        try:
            notif = Notificacion.objects.get(id=notificacion_id, usuario=user)
        except Notificacion.DoesNotExist:
            raise Exception("Notificación no encontrada")

        if notif.leida:
            return MarcarNotificacionLeida(ok=True, notificacion=notif)
        
        notif.leida = True
        notif.save()
        return MarcarNotificacionLeida(ok=True, notificacion=notif)


class MarcarTodasNotificacionesLeidas(graphene.Mutation):
    ok = graphene.Boolean()
    total = graphene.Int()

    @login_required
    def mutate(self, info):
        user = info.context.user
        actualizadas = Notificacion.objects.filter(usuario=user, leida=False).update(leida=True)
        return MarcarTodasNotificacionesLeidas(ok=True, total=actualizadas)
    
    

# ===== MUTACIONES PRINCIPALES =====

class MutationUser(graphene.ObjectType):
    # Mutaciones de usuario existentes
    login_usuario = LoginUsuario.Field()
    registro_usuario = RegistroUsuario.Field()
    editar_perfil = EditarPerfil.Field()
    cambiar_contrasena = CambiarContrasena.Field()
    activar_vendedor = ActivarVendedor.Field()

    # Nuevas mutaciones de tienda
    crear_tienda = CrearTienda.Field()
    editar_tienda = EditarTienda.Field()
    eliminar_tienda = EliminarTienda.Field()

    # Mutaciones de producto
    crear_producto = CrearProducto.Field()
    editar_producto = EditarProducto.Field()
    eliminar_producto = EliminarProducto.Field()

    # Nuevas mutaciones de variantes
    crear_variante = CrearVariante.Field()
    editar_variante = EditarVariante.Field()
    eliminar_variante = EliminarVariante.Field()

    # Nuevas mutaciones de imágenes
    subir_imagen = SubirImagenProducto.Field()
    subir_imagen_variante = SubirImagenVariante.Field()
    eliminar_imagen = EliminarImagen.Field()
    actualizar_orden_imagen = ActualizarOrdenImagen.Field()
    
    # Nuevas mutaciones de favoritos
    agregar_favorito = AgregarFavorito.Field()
    eliminar_favorito = EliminarFavorito.Field()    
    
    # Nuevas mutaciones de Seguir
    seguir_tienda = SeguirTienda.Field()
    dejar_seguir_tienda = DejarDeSeguirTienda.Field()
    
    # Nuevas mutaciones de Notificaciones
    marcar_notificacion = MarcarNotificacionLeida.Field()