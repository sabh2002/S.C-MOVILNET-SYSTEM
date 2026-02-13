from django.contrib import admin
from .models import (
    Marca, Proveedor, Cliente, Producto,
    PerfilEmpleado, Bitacora, TipoInventario, MovimientoInventario,
    Cotizacion, DetalleCotizacion, OrdenCompra, DetalleOrdenCompra,
    NotaEntrega, DetalleNotaEntrega
)

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nombre_marca', 'estado', 'fecha_registro')
    list_filter = ('estado', 'fecha_registro')
    search_fields = ('nombre_marca',)
    ordering = ('nombre_marca',)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rif', 'telefono', 'email', 'estado', 'fecha_registro')
    list_filter = ('estado', 'fecha_registro')
    search_fields = ('nombre', 'rif', 'email')
    ordering = ('nombre',)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cedula', 'telefono', 'fecha_registro')
    list_filter = ('fecha_registro',)
    search_fields = ('nombre', 'cedula', 'telefono')
    ordering = ('nombre',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'marca', 'precio', 'stock_actual', 'estado', 'necesita_reposicion', 'fecha_registro')
    list_filter = ('estado', 'marca', 'fecha_registro')
    search_fields = ('nombre', 'marca__nombre_marca')
    ordering = ('nombre',)
    
    def necesita_reposicion(self, obj):
        return obj.necesita_reposicion
    necesita_reposicion.boolean = True
    necesita_reposicion.short_description = 'Necesita Reposición'


@admin.register(PerfilEmpleado)
class PerfilEmpleadoAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol')
    list_filter = ('rol',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'tabla_afectada', 'accion_realizada', 'cod_registro_afectado', 'fecha_hora')
    list_filter = ('tabla_afectada', 'accion_realizada', 'fecha_hora')
    search_fields = ('tabla_afectada', 'descripcion')
    readonly_fields = ('fecha_hora',)


@admin.register(TipoInventario)
class TipoInventarioAdmin(admin.ModelAdmin):
    list_display = ('tipo_movimiento', 'categoria_movimiento')
    search_fields = ('tipo_movimiento', 'categoria_movimiento')


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tipo_inventario', 'cantidad', 'empleado', 'fecha_movimiento')
    list_filter = ('tipo_inventario', 'fecha_movimiento')
    search_fields = ('producto__nombre', 'observaciones')


class DetalleCotizacionInline(admin.TabularInline):
    model = DetalleCotizacion
    extra = 1


@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'proveedor', 'fecha_cotizacion', 'total', 'estado', 'validez_dias')
    list_filter = ('estado', 'fecha_cotizacion')
    search_fields = ('proveedor__nombre',)
    inlines = [DetalleCotizacionInline]


class DetalleOrdenCompraInline(admin.TabularInline):
    model = DetalleOrdenCompra
    extra = 1


@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('numero_orden', 'cotizacion', 'fecha_orden', 'fecha_registro')
    list_filter = ('fecha_orden',)
    search_fields = ('numero_orden',)
    inlines = [DetalleOrdenCompraInline]


class DetalleNotaEntregaInline(admin.TabularInline):
    model = DetalleNotaEntrega
    extra = 1


@admin.register(NotaEntrega)
class NotaEntregaAdmin(admin.ModelAdmin):
    list_display = ('numero_entrega', 'cliente', 'subtotal', 'descuento', 'total', 'fecha_registro')
    list_filter = ('fecha_registro',)
    search_fields = ('numero_entrega', 'cliente__nombre')
    inlines = [DetalleNotaEntregaInline]
