import graphene
from graphene_django.types import DjangoObjectType
from apps.common.models import CustomUser, Tienda, Categoria, Producto, Variante, Imagen
from django.contrib.auth.hashers import make_password
from graphql import GraphQLError
from ..auth import decode_jwt, generate_jwt
from ..validador import admin_required
from django.contrib.auth import authenticate
from graphene_file_upload.scalars import Upload
from ..scalars import Decimal

# Tipos de objetos para GraphQL
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
    precioBase = Decimal()
    class Meta:
        model = Producto
        fields = "__all__"

class VarianteType(DjangoObjectType):
    class Meta:
        model = Variante
        fields = "__all__"

# --- LOGIN ---
class Login(graphene.Mutation):
    token = graphene.String()
    user_id = graphene.Int()
    email = graphene.String()
    username = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, email, password):
        user = authenticate(request=info.context,username=email, password=password)
        if user is None:
            raise GraphQLError("Correo o contraseña incorrectos.")
        if not (user.is_staff or user.is_superuser):
            raise GraphQLError("El usuario no tiene permisos de administrador.")
        token = generate_jwt(user)
        return Login(
            token=token,
            user_id=user.id,
            email=user.email,
            username=user.username
        )

# --- USUARIOS ---
# Crear usuario administrador
class CrearAdmin(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    admin_id = graphene.Int()

    class Arguments:
        email = graphene.String(required=True)
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        nombre = graphene.String(required=True)
        apellidos = graphene.String(required=True)
        celular = graphene.String()
    @admin_required
    def mutate(self, info, email, username, password, nombre, apellidos, celular=None):
        if CustomUser.objects.filter(email=email).exists():
            raise GraphQLError("Este correo ya está registrado.")
        if CustomUser.objects.filter(username=username).exists():
            raise GraphQLError("Este nombre de usuario ya está en uso.")

        admin = CustomUser.objects.create_superuser(
            email=email,
            username=username,
            password=password,
            nombre=nombre,
            apellidos=apellidos,
            celular=celular,
        )
        return CrearAdmin(ok=True, message="Administrador creado correctamente", admin_id=admin.id)

# Crear usuario normal
class CreateUser(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    user_id = graphene.Int()

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        username = graphene.String(required=True)
        nombre = graphene.String(required=True)
        apellidos = graphene.String(required=True)
        celular = graphene.String(required=True)

    def mutate(self, info, email, password, username, nombre, apellidos, celular=None):
        if CustomUser.objects.filter(email=email).exists():
            raise GraphQLError("Correo en uso.")
        if CustomUser.objects.filter(username=username).exists():
            raise GraphQLError("El nombre de usuario ya está en uso.")
        user = CustomUser.objects.create_user(
            email=email,
            username=username,
            password=password,
            nombre=nombre or "",
            apellidos=apellidos or "",
            celular=celular or "",
            is_staff=False,
            is_seller=False,
        )
        return CreateUser(ok=True, message="Usuario creado correctamente.", user_id=user.id)

# Actualizar usuario
class UpdateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        id = graphene.ID(required=True)
        email = graphene.String()
        password = graphene.String()
        username = graphene.String()
        nombre = graphene.String()
        apellidos = graphene.String()
        is_staff = graphene.Boolean()

    @admin_required
    def mutate(self, info, id, **kwargs):
        try:
            user = CustomUser.objects.get(pk=id)
        except CustomUser.DoesNotExist:
            raise GraphQLError("Usuario no encontrado")

        if "email" in kwargs and kwargs["email"]:
            if CustomUser.objects.filter(email=kwargs["email"]).exclude(pk=id).exists():
                raise GraphQLError("El correo ya está en uso por otro usuario.")
            user.email = kwargs["email"]

        if "username" in kwargs and kwargs["username"]:
            if CustomUser.objects.filter(username=kwargs["username"]).exclude(pk=id).exists():
                raise GraphQLError("El nombre de usuario ya está en uso por otro usuario.")
            user.username = kwargs["username"]

        if "password" in kwargs and kwargs["password"]:
            user.password = make_password(kwargs["password"])

        for attr in ["nombre", "apellidos", "is_staff"]:
            if attr in kwargs and kwargs[attr] is not None:
                setattr(user, attr, kwargs[attr])

        user.save()
        return UpdateUser(user=user)

# Eliminar usuario
class DeleteUser(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    @admin_required
    def mutate(self, info, id):
        try:
            user = CustomUser.objects.get(pk=id)
            user.delete()
            return DeleteUser(ok=True)
        except CustomUser.DoesNotExist:
            raise GraphQLError("Usuario no encontrado")

# Estados Usuarios
class CambiarContrasena(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    
    class Arguments:
        id = graphene.ID(required=True)
        old_password = graphene.String(required=True)
        new_password = graphene.String(required=True)

    @staticmethod
    def mutate(root, info, id, old_password, new_password):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("No autorizado")

        # Solo el mismo usuario o admin puede cambiar la contraseña
        if str(user.id) != id and not user.is_staff:
            raise GraphQLError("No tiene permiso para cambiar esta contraseña")

        try:
            target_user = CustomUser.objects.get(pk=id)
        except CustomUser.DoesNotExist:
            raise GraphQLError("Usuario no encontrado")

        if not target_user.check_password(old_password):
            raise GraphQLError("Contraseña actual incorrecta")

        if len(new_password) < 8:
            raise GraphQLError("La nueva contraseña debe tener al menos 8 caracteres.")

        target_user.password = make_password(new_password)
        target_user.save()

        return CambiarContrasena(ok=True, message="Contraseña actualizada correctamente.")
    
# --- TIENDAS ---
class CreateTienda(graphene.Mutation):
    tienda = graphene.Field(TiendaType)

    class Arguments:
        nombre = graphene.String(required=True)
        propietario_id = graphene.ID(required=True)

    @admin_required
    def mutate(self, info, nombre, propietario_id):
        try:
            propietario = CustomUser.objects.get(pk=propietario_id)
        except CustomUser.DoesNotExist:
            raise GraphQLError("Propietario no encontrado")
        tienda = Tienda.objects.create(nombre=nombre, propietario=propietario)
        return CreateTienda(tienda=tienda)
# Actualizar tiendas
class UpdateTienda(graphene.Mutation):
    tienda = graphene.Field(TiendaType)

    class Arguments:
        id = graphene.ID(required=True)
        nombre = graphene.String()

    @admin_required
    def mutate(self, info, id, nombre=None):
        try:
            tienda = Tienda.objects.get(pk=id)
        except Tienda.DoesNotExist:
            raise GraphQLError("Tienda no encontrada")
        if nombre and nombre.strip():
            tienda.nombre = nombre.strip()
            tienda.save()
        return UpdateTienda(tienda=tienda)
# Eliminar tiendas
class DeleteTienda(graphene.Mutation):
    ok = graphene.Boolean()
    massage = graphene

    class Arguments:
        id = graphene.ID(required=True)

    @admin_required
    def mutate(self, info, id):
        try:
            tienda = Tienda.objects.get(pk=id)
            tienda.delete()
            return DeleteTienda(ok=True)
        except Tienda.DoesNotExist:
            raise GraphQLError("Tienda no encontrada")
        
        if tienda.estado == 'Pendiente de Eliminación':
            tienda.delete()
            return DeleteTienda(ok=True, message="Tienda eliminada correctamente")
        else:
            tienda.estado = 'Pendiente de Eliminación'
            tienda.fecha_eliminacion = timezone.now() + timezone.timedelta(days=7)
            tienda.save()
            return DeleteTienda(ok=False, message="Tienda marcada para eliminación(7 dias).")
# --- CATEGORÍAS ---
class CreateCategoria(graphene.Mutation):
    categoria = graphene.Field(CategoriaType)
    ok = graphene.Boolean()
    message = graphene.String()
    class Arguments:
        nombre = graphene.String(required=True)
        icono = graphene.String(required=False)
        color = graphene.String(required=False)
        categoria_padre_id = graphene.Int(required=False)

    @admin_required
    def mutate(self, info, nombre, icono=None, color=None, categoria_padre_id=None):
        if not nombre.strip():
            raise GraphQLError("El nombre de la categoría no puede estar vacío.")

        categoria_padre = None
        if categoria_padre_id:
            try:
                categoria_padre = Categoria.objects.get(id=categoria_padre_id)
            except Categoria.DoesNotExist:
                raise GraphQLError("La categoría padre no existe.")

        categoria = Categoria.objects.create(nombre=nombre.strip(),icono=icono,color=color,categoriaPadre=categoria_padre)
        return CreateCategoria(ok=True,message="Categoría creada correctamente",categoria=categoria)
class UpdateCategoria(graphene.Mutation):
    categoria = graphene.Field(CategoriaType)
    ok = graphene.Boolean()
    message = graphene.String()
    class Arguments:
        id = graphene.ID(required=True)
        nombre = graphene.String()
        icono = graphene.String(required=False)
        color = graphene.String(required=False)
        categoria_padre_id = graphene.Int(required=False)

    @admin_required
    def mutate(self, info, id, nombre=None, icono=None, color=None, categoria_padre_id=None):
        try:
            categoria = Categoria.objects.get(pk=id)
        except Categoria.DoesNotExist:
            raise GraphQLError("Categoría no encontrada")
        
        if nombre is not None:
            categoria.nombre = nombre.strip()
            if not nombre:
                raise GraphQLError("El nombre de la categoría no puede estar vacío.")
            categoria.nombre = nombre
            
        if icono is not None:
            categoria.icono = icono
            
        if color is not None:
            categoria.color = color
            
        if categoria_padre_id is not None:
            if categoria_padre_id == id:
                raise GraphQLError("Una categoría no puede ser su propia padre.")
            try:
                categoria_padre = Categoria.objects.get(id=categoria_padre_id)
                categoria.categoriaPadre = categoria_padre
            except Categoria.DoesNotExist:
                raise GraphQLError("La categoría padre no existe.")
            
        categoria.save()
        
        return UpdateCategoria(ok=True,message="Categoria Actualizda",categoria=categoria)

class DeleteCategoria(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        id = graphene.ID(required=True)

    @admin_required
    def mutate(self, info, id):
        try:
            categoria = Categoria.objects.get(pk=id)
            categoria.delete()
            return DeleteCategoria(ok=True, message="Categoría eliminada correctamente")
        except Categoria.DoesNotExist:
            raise GraphQLError("Categoría no encontrada")

# --- PRODUCTOS ---
class CreateProducto(graphene.Mutation):
    producto = graphene.Field(ProductoType)

    class Arguments:
        nombre = graphene.String(required=True)
        precioBase = Decimal(required=True)
        tienda_id = graphene.ID(required=True)
        categoria_id = graphene.ID()

    @admin_required
    def mutate(self, info, nombre, precioBase, tienda_id, categoria_id=None):
        if not nombre.strip():
            raise GraphQLError("El nombre del producto no puede estar vacío.")
        try:
            tienda = Tienda.objects.get(pk=tienda_id)
        except Tienda.DoesNotExist:
            raise GraphQLError("Tienda no encontrada")

        categoria = None
        if categoria_id:
            try:
                categoria = Categoria.objects.get(pk=categoria_id)
            except Categoria.DoesNotExist:
                raise GraphQLError("Categoría no encontrada")

        producto = Producto.objects.create(
            nombre=nombre.strip(),
            precioBase=precioBase,
            tienda=tienda,
            categoria=categoria
        )
        return CreateProducto(producto=producto)

class UpdateProducto(graphene.Mutation):
    producto = graphene.Field(ProductoType)

    class Arguments:
        id = graphene.ID(required=True)
        nombre = graphene.String()
        precioBase = Decimal()
        estado = graphene.String()
        categoria_id = graphene.ID()

    @admin_required
    def mutate(self, info, id, **kwargs):
        try:
            producto = Producto.objects.get(pk=id)
        except Producto.DoesNotExist:
            raise GraphQLError("Producto no encontrado")

        if "nombre" in kwargs and kwargs["nombre"]:
            if kwargs["nombre"].strip():
                producto.nombre = kwargs["nombre"].strip()
            else:
                raise GraphQLError("El nombre del producto no puede estar vacío.")
        if "precioBase" in kwargs and kwargs["precioBase"] is not None:
            producto.precioBase = kwargs["precioBase"]
        if "estado" in kwargs and kwargs["estado"]:
            if kwargs["estado"] in dict(producto.estados):
                producto.estado = kwargs["estado"]
            else:
                raise GraphQLError("Estado inválido. Debe ser uno de: " + ", ".join(dict(producto.estados).keys()))
        if "categoria_id" in kwargs and kwargs["categoria_id"]:
            try:
                categoria = Categoria.objects.get(pk=kwargs["categoria_id"])
                producto.categoria = categoria
            except Categoria.DoesNotExist:
                raise GraphQLError("Categoría no encontrada")
        producto.save()
        return UpdateProducto(producto=producto)

class DeleteProducto(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    @admin_required
    def mutate(self, info, id):
        try:
            producto = Producto.objects.get(pk=id)
            producto.delete()
            return DeleteProducto(ok=True)
        except Producto.DoesNotExist:
            raise GraphQLError("Producto no encontrado")

# --- VARIANTES ---
class CreateVariante(graphene.Mutation):
    variante = graphene.Field(VarianteType)

    class Arguments:
        producto_id = graphene.ID(required=True)
        talla = graphene.String(required=True)
        color = graphene.String()
        precio = Decimal(required=True)
        stock = graphene.Int(required=True)

    @admin_required
    def mutate(self, info, producto_id, talla, precio, stock, color=None):
        if not talla.strip():
            raise GraphQLError("La talla no puede estar vacía.")
        if precio is None or precio < 0:
            raise GraphQLError("El precio debe ser un número positivo.")
        if stock is None or stock < 0:
            raise GraphQLError("El stock debe ser un número positivo.")
        try:
            producto = Producto.objects.get(pk=producto_id)
        except Producto.DoesNotExist:
            raise GraphQLError("Producto no encontrado")

        variante = Variante.objects.create(
            producto=producto,
            talla=talla.strip(),
            color=color,
            precio=precio,
            stock=stock
        )
        return CreateVariante(variante=variante)

class UpdateVariante(graphene.Mutation):
    variante = graphene.Field(VarianteType)

    class Arguments:
        id = graphene.ID(required=True)
        talla = graphene.String()
        color = graphene.String()
        precio = Decimal()
        stock = graphene.Int()

    @admin_required
    def mutate(self, info, id, **kwargs):
        try:
            variante = Variante.objects.get(pk=id)
        except Variante.DoesNotExist:
            raise GraphQLError("Variante no encontrada")

        if "talla" in kwargs and kwargs["talla"]:
            if kwargs["talla"].strip():
                variante.talla = kwargs["talla"].strip()
            else:
                raise GraphQLError("La talla no puede estar vacía.")
        if "color" in kwargs:
            variante.color = kwargs["color"]
        if "precio" in kwargs and kwargs["precio"] is not None:
            if kwargs["precio"] < 0:
                raise GraphQLError("El precio debe ser un número positivo.")
            variante.precio = kwargs["precio"]
        if "stock" in kwargs and kwargs["stock"] is not None:
            if kwargs["stock"] < 0:
                raise GraphQLError("El stock debe ser un número positivo.")
            variante.stock = kwargs["stock"]

        variante.save()
        return UpdateVariante(variante=variante)

class DeleteVariante(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    @admin_required
    def mutate(self, info, id):
        try:
            variante = Variante.objects.get(pk=id)
            variante.delete()
            return DeleteVariante(ok=True)
        except Variante.DoesNotExist:
            raise GraphQLError("Variante no encontrada")
        
# Imagenes
class ImagenType(DjangoObjectType):
    class Meta:
        model = Imagen
        fields = "__all__"

# Crear Imagen
class CreateImagen(graphene.Mutation):
    imagen = graphene.Field(ImagenType)

    class Arguments:
        nombre = graphene.String(required=True)
        archivo = Upload(required=True)
        esPrincipal = graphene.Boolean()
        orden = graphene.Int()
        producto_id = graphene.ID()
        variante_id = graphene.ID()

    @admin_required
    def mutate(self, info, archivo, esPrincipal=False, orden=0, nombre=None, producto_id=None, variante_id=None):
        if not producto_id and not variante_id:
            raise GraphQLError("Debe proporcionar una imagen.")
        if producto_id and variante_id:
            raise GraphQLError("No puede asociar la misma imagen.")

        imagen = Imagen(
            nombre=nombre,
            archivo=archivo,
            esPrincipal=esPrincipal,
            orden=orden
        )

        if producto_id:
            try:
                imagen.producto = Producto.objects.get(pk=producto_id)
            except Producto.DoesNotExist:
                raise GraphQLError("Producto no encontrado")
        
        if producto_id:
            try:
                producto = Producto.objects.get(pk=producto_id)
                imagen.producto = producto
            except Producto.DoesNotExist:
                raise GraphQLError("Producti no encontrada")
        if variante_id:
            try:
                variante = Variante.objects.get(pk=variante_id)
                imagen.variante = variante
            except Variante.DoesNotExist:
                raise GraphQLError("Variante no encontrada")

        imagen.save()
        return CreateImagen(imagen=imagen)
  
# Actualizar Imagen  
class UpdateImagen(graphene.Mutation):
    imagen = graphene.Field(ImagenType)

    class Arguments:
        id = graphene.ID(required=True)
        nombre = graphene.String()
        archivo = Upload()
        esPrincipal = graphene.Boolean()
        orden = graphene.Int()

    @admin_required
    def mutate(self, info, id, **kwargs):
        try:
            imagen = Imagen.objects.get(pk=id)
        except Imagen.DoesNotExist:
            raise GraphQLError("Imagen no encontrada.")

        for field in ["nombre", "esPrincipal", "orden"]:
            if field in kwargs and kwargs[field] is not None:
                setattr(imagen, field, kwargs[field])

        if "archivo" in kwargs and kwargs["archivo"]:
            imagen.archivo = kwargs["archivo"]

        imagen.save()
        return UpdateImagen(imagen=imagen)

# Eliminar Imagen
class DeleteImagen(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    @admin_required
    def mutate(self, info, id):
        try:
            imagen = Imagen.objects.get(pk=id)
            imagen.delete()
            return DeleteImagen(ok=True)
        except Imagen.DoesNotExist:
            raise GraphQLError("Imagen no encontrada.")
        


# Mutations Root
class MutationAdmin(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()
    cambiar_contrasena = CambiarContrasena.Field()

    create_tienda = CreateTienda.Field()
    update_tienda = UpdateTienda.Field()
    delete_tienda = DeleteTienda.Field()

    create_categoria = CreateCategoria.Field()
    update_categoria = UpdateCategoria.Field()
    delete_categoria = DeleteCategoria.Field()

    create_producto = CreateProducto.Field()
    update_producto = UpdateProducto.Field()
    delete_producto = DeleteProducto.Field()

    create_variante = CreateVariante.Field()
    update_variante = UpdateVariante.Field()
    delete_variante = DeleteVariante.Field()
    
    create_imagen = CreateImagen.Field()
    update_imagen = UpdateImagen.Field()
    delete_imagen = DeleteImagen.Field()
    
    crear_usuario = CreateUser.Field()
    crear_admin = CrearAdmin.Field()
    
    login = Login.Field()

