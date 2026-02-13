from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator
from django.core.exceptions import ValidationError

# Validadores personalizados
cedula_validator = RegexValidator(
    regex=r'^[VEJPG]-\d{6,8}$',
    message='La cédula debe tener el formato: V-12345678, E-1234567, J-12345678, P-123456 o G-12345678'
)

rif_validator = RegexValidator(
    regex=r'^[VEJPG]-\d{10}$',
    message='El RIF debe tener el formato: J-1234567890, V-1234567890, E-1234567890, P-1234567890 o G-1234567890'
)

class Marca(models.Model):
    """Modelo para gestionar las marcas de productos"""
    nombre_marca = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Marca")
    estado = models.BooleanField(default=True, verbose_name="Activo")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    
    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ['nombre_marca']
    
    def __str__(self):
        return self.nombre_marca


class Proveedor(models.Model):
    """Modelo para gestionar los proveedores"""
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Proveedor")
    rif = models.CharField(
        max_length=13, 
        unique=True, 
        validators=[rif_validator],
        verbose_name="RIF",
        help_text="Formato: J-1234567890"
    )
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(verbose_name="Correo Electrónico", blank=True, null=True)
    direccion = models.TextField(verbose_name="Dirección")
    estado = models.BooleanField(default=True, verbose_name="Activo")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.rif})"


class Cliente(models.Model):
    """Modelo para gestionar los clientes"""
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Cliente")
    cedula = models.CharField(
        max_length=11, 
        unique=True, 
        validators=[cedula_validator],
        verbose_name="Cédula",
        help_text="Formato: V-12345678"
    )
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    direccion = models.TextField(verbose_name="Dirección", blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.cedula})"


class Producto(models.Model):
    """Modelo para gestionar los productos"""
    marca = models.ForeignKey(
        Marca, 
        on_delete=models.PROTECT, 
        verbose_name="Marca",
        related_name="productos"
    )
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    descripcion_caracteristicas = models.TextField(
        verbose_name="Descripción y Características",
        blank=True,
        null=True
    )
    precio = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name="Precio ($)"
    )
    estado = models.BooleanField(default=True, verbose_name="Activo")
    stock_actual = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0)],
        verbose_name="Stock Actual"
    )
    stock_minimo = models.IntegerField(
        default=5, 
        validators=[MinValueValidator(0)],
        verbose_name="Stock Mínimo"
    )
    stock_maximo = models.IntegerField(
        default=100, 
        validators=[MinValueValidator(0)],
        verbose_name="Stock Máximo"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.marca.nombre_marca}"
    
    def clean(self):
        """Validación personalizada para stocks"""
        if self.stock_minimo > self.stock_maximo:
            raise ValidationError({
                'stock_minimo': 'El stock mínimo no puede ser mayor que el stock máximo.'
            })
        if self.stock_actual > self.stock_maximo:
            raise ValidationError({
                'stock_actual': 'El stock actual no puede ser mayor que el stock máximo.'
            })
    
    @property
    def necesita_reposicion(self):
        """Indica si el producto necesita reposición"""
        return self.stock_actual < self.stock_minimo

    @property
    def umbral_bajo(self):
        """Umbral para considerar stock como 'bajo' (20% sobre el mínimo)"""
        return self.stock_minimo + max(1, int(self.stock_minimo * 0.2))

    @property
    def umbral_cerca_maximo(self):
        """Umbral para considerar stock 'cerca del máximo' (90% del máximo)"""
        return int(self.stock_maximo * 0.9)

    @property
    def estado_stock(self):
        """Retorna el estado del stock con descripciones detalladas"""
        if self.stock_actual == 0:
            return "Sin Stock"
        elif self.stock_actual < self.stock_minimo:
            return "Agotándose"
        elif self.stock_actual <= self.umbral_bajo:
            return "Stock Bajo"
        elif self.stock_actual >= self.stock_maximo:
            return "Stock Máximo"
        elif self.stock_actual >= self.umbral_cerca_maximo:
            return "Cerca del Máximo"
        else:
            return "Stock Normal"

    @property
    def css_estado_stock(self):
        """Retorna clase CSS según el estado del stock"""
        estado = self.estado_stock
        if estado in ("Sin Stock", "Agotándose"):
            return "danger"
        elif estado == "Stock Bajo":
            return "warning"
        elif estado in ("Cerca del Máximo", "Stock Máximo"):
            return "info"
        return "success"


class PerfilEmpleado(models.Model):
    """Modelo para gestionar los perfiles de empleados"""
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('empleado', 'Empleado'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='empleado', verbose_name="Rol")
    animal_favorito = models.CharField(max_length=100, verbose_name="Animal Favorito")
    color_favorito = models.CharField(max_length=100, verbose_name="Color Favorito")

    class Meta:
        verbose_name = "Perfil de Empleado"
        verbose_name_plural = "Perfiles de Empleados"
        ordering = ['user__username']

    def __str__(self):
        return f"{self.user.username} - {self.get_rol_display()}"


class Bitacora(models.Model):
    """Modelo para registrar la bitácora de acciones del sistema"""
    empleado = models.ForeignKey(PerfilEmpleado, on_delete=models.SET_NULL, null=True, verbose_name="Empleado", related_name="bitacoras")
    tabla_afectada = models.CharField(max_length=100, verbose_name="Tabla Afectada")
    accion_realizada = models.CharField(max_length=50, verbose_name="Acción Realizada")
    cod_registro_afectado = models.IntegerField(verbose_name="Código Registro Afectado")
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")
    descripcion = models.TextField(verbose_name="Descripción", blank=True, null=True)

    class Meta:
        verbose_name = "Bitácora"
        verbose_name_plural = "Bitácoras"
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"{self.accion_realizada} en {self.tabla_afectada} - {self.fecha_hora}"


class TipoInventario(models.Model):
    """Modelo para tipos de movimiento de inventario"""
    tipo_movimiento = models.CharField(max_length=50, verbose_name="Tipo de Movimiento")
    categoria_movimiento = models.CharField(max_length=50, verbose_name="Categoría de Movimiento")

    class Meta:
        verbose_name = "Tipo de Inventario"
        verbose_name_plural = "Tipos de Inventario"
        ordering = ['tipo_movimiento']

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.categoria_movimiento}"


class MovimientoInventario(models.Model):
    """Modelo para registrar movimientos de inventario"""
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, verbose_name="Producto", related_name="movimientos")
    tipo_inventario = models.ForeignKey(TipoInventario, on_delete=models.PROTECT, verbose_name="Tipo de Inventario", related_name="movimientos")
    cantidad = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Cantidad")
    empleado = models.ForeignKey(PerfilEmpleado, on_delete=models.SET_NULL, null=True, verbose_name="Empleado", related_name="movimientos")
    fecha_movimiento = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Movimiento")
    observaciones = models.TextField(verbose_name="Observaciones", blank=True, null=True)

    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ['-fecha_movimiento']

    def __str__(self):
        return f"{self.tipo_inventario} - {self.producto.nombre} ({self.cantidad})"


class Cotizacion(models.Model):
    """Modelo para gestionar cotizaciones de proveedores"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('vencida', 'Vencida'),
    ]

    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, verbose_name="Proveedor", related_name="cotizaciones")
    fecha_cotizacion = models.DateField(verbose_name="Fecha de Cotización")
    validez_dias = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Validez (días)")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Total")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente', verbose_name="Estado")
    observaciones = models.TextField(verbose_name="Observaciones", blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Cotización"
        verbose_name_plural = "Cotizaciones"
        ordering = ['-fecha_cotizacion']

    def __str__(self):
        return f"COT-{self.pk} - {self.proveedor.nombre}"


class DetalleCotizacion(models.Model):
    """Modelo para los detalles de cada cotización"""
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, verbose_name="Cotización", related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, verbose_name="Producto", related_name="detalles_cotizacion")
    cantidad = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Cantidad")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Detalle de Cotización"
        verbose_name_plural = "Detalles de Cotización"

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"


class OrdenCompra(models.Model):
    """Modelo para gestionar órdenes de compra"""
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.PROTECT, verbose_name="Cotización", related_name="ordenes_compra")
    numero_orden = models.CharField(max_length=50, unique=True, verbose_name="Número de Orden")
    fecha_orden = models.DateField(verbose_name="Fecha de Orden")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Orden de Compra"
        verbose_name_plural = "Órdenes de Compra"
        ordering = ['-fecha_orden']

    def __str__(self):
        return f"OC-{self.numero_orden}"


class DetalleOrdenCompra(models.Model):
    """Modelo para los detalles de cada orden de compra"""
    orden_compra = models.ForeignKey(OrdenCompra, on_delete=models.CASCADE, verbose_name="Orden de Compra", related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, verbose_name="Producto", related_name="detalles_orden_compra")
    cantidad_solicitada = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Cantidad Solicitada")
    cantidad_recibida = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name="Cantidad Recibida")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Detalle de Orden de Compra"
        verbose_name_plural = "Detalles de Orden de Compra"

    def __str__(self):
        return f"{self.producto.nombre} - Solicitado: {self.cantidad_solicitada}, Recibido: {self.cantidad_recibida}"


class NotaEntrega(models.Model):
    """Modelo para gestionar notas de entrega a clientes"""
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, verbose_name="Cliente", related_name="notas_entrega")
    numero_entrega = models.CharField(max_length=50, unique=True, verbose_name="Número de Entrega")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Subtotal")
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Descuento")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Total")
    observaciones = models.TextField(verbose_name="Observaciones", blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Nota de Entrega"
        verbose_name_plural = "Notas de Entrega"
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"NE-{self.numero_entrega} - {self.cliente.nombre}"


class DetalleNotaEntrega(models.Model):
    """Modelo para los detalles de cada nota de entrega"""
    nota_entrega = models.ForeignKey(NotaEntrega, on_delete=models.CASCADE, verbose_name="Nota de Entrega", related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, verbose_name="Producto", related_name="detalles_nota_entrega")
    cantidad = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Precio Unitario")
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Descuento")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Subtotal")

    class Meta:
        verbose_name = "Detalle de Nota de Entrega"
        verbose_name_plural = "Detalles de Nota de Entrega"

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad} - {self.subtotal}"
