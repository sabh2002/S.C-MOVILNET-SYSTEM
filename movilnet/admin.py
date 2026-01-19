from django.contrib import admin
from .models import Marca, Proveedor, Cliente, Producto

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
