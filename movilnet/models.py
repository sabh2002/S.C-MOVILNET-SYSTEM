from django.db import models
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
        return self.stock_actual <= self.stock_minimo
    
    @property
    def estado_stock(self):
        """Retorna el estado del stock"""
        if self.stock_actual == 0:
            return "Sin Stock"
        elif self.stock_actual <= self.stock_minimo:
            return "Stock Bajo"
        elif self.stock_actual >= self.stock_maximo:
            return "Stock Completo"
        else:
            return "Stock Normal"
