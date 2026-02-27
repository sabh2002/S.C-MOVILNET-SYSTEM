from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cambiar-password/', views.cambiar_password_view, name='cambiar_password'),
    path('recuperar-password/', views.recuperar_password_view, name='recuperar_password'),
    path('nueva-password/', views.nueva_password_view, name='nueva_password'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('empleados/', views.lista_empleados_view, name='lista_empleados'),
    path('empleados/registro/', views.registro_empleado_view, name='registro_empleado'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # URLs Marca
    path('marcas/', views.MarcaListView.as_view(), name='marca_list'),
    path('marcas/crear/', views.MarcaCreateView.as_view(), name='marca_create'),
    path('marcas/editar/<int:pk>/', views.MarcaUpdateView.as_view(), name='marca_update'),
    path('marcas/eliminar/<int:pk>/', views.MarcaDeleteView.as_view(), name='marca_delete'),

    # URLs Proveedor
    path('proveedores/', views.ProveedorListView.as_view(), name='proveedor_list'),
    path('proveedores/crear/', views.ProveedorCreateView.as_view(), name='proveedor_create'),
    path('proveedores/editar/<int:pk>/', views.ProveedorUpdateView.as_view(), name='proveedor_update'),
    path('proveedores/eliminar/<int:pk>/', views.ProveedorDeleteView.as_view(), name='proveedor_delete'),

    # URLs Cliente
    path('clientes/', views.ClienteListView.as_view(), name='cliente_list'),
    path('clientes/crear/', views.ClienteCreateView.as_view(), name='cliente_create'),
    path('clientes/editar/<int:pk>/', views.ClienteUpdateView.as_view(), name='cliente_update'),
    path('clientes/eliminar/<int:pk>/', views.ClienteDeleteView.as_view(), name='cliente_delete'),

    # URLs Producto
    path('productos/', views.ProductoListView.as_view(), name='producto_list'),
    path('productos/crear/', views.ProductoCreateView.as_view(), name='producto_create'),
    path('productos/editar/<int:pk>/', views.ProductoUpdateView.as_view(), name='producto_update'),
    path('productos/eliminar/<int:pk>/', views.ProductoDeleteView.as_view(), name='producto_delete'),

    # URLs Tipo Inventario
    path('inventario/tipos/', views.TipoInventarioListView.as_view(), name='tipo_inventario_list'),
    path('inventario/tipos/crear/', views.TipoInventarioCreateView.as_view(), name='tipo_inventario_create'),
    path('inventario/tipos/editar/<int:pk>/', views.TipoInventarioUpdateView.as_view(), name='tipo_inventario_update'),
    path('inventario/tipos/eliminar/<int:pk>/', views.TipoInventarioDeleteView.as_view(), name='tipo_inventario_delete'),

    # URLs Movimientos de Inventario
    path('inventario/movimientos/', views.MovimientoInventarioListView.as_view(), name='movimiento_list'),
    path('inventario/movimientos/crear/', views.MovimientoInventarioCreateView.as_view(), name='movimiento_create'),

    # URLs Cotización
    path('cotizaciones/', views.CotizacionListView.as_view(), name='cotizacion_list'),
    path('cotizaciones/crear/', views.CotizacionCreateView.as_view(), name='cotizacion_create'),
    path('cotizaciones/<int:pk>/', views.CotizacionDetailView.as_view(), name='cotizacion_detail'),
    path('cotizaciones/editar/<int:pk>/', views.CotizacionUpdateView.as_view(), name='cotizacion_update'),
    path('cotizaciones/eliminar/<int:pk>/', views.CotizacionDeleteView.as_view(), name='cotizacion_delete'),

    # URLs Orden de Compra
    path('ordenes-compra/', views.OrdenCompraListView.as_view(), name='orden_compra_list'),
    path('ordenes-compra/crear/', views.OrdenCompraCreateView.as_view(), name='orden_compra_create'),
    path('ordenes-compra/<int:pk>/', views.OrdenCompraDetailView.as_view(), name='orden_compra_detail'),
    path('ordenes-compra/editar/<int:pk>/', views.OrdenCompraUpdateView.as_view(), name='orden_compra_update'),
    path('ordenes-compra/eliminar/<int:pk>/', views.OrdenCompraDeleteView.as_view(), name='orden_compra_delete'),

    # URLs Nota de Entrega
    path('notas-entrega/', views.NotaEntregaListView.as_view(), name='nota_entrega_list'),
    path('notas-entrega/crear/', views.NotaEntregaCreateView.as_view(), name='nota_entrega_create'),
    path('notas-entrega/<int:pk>/', views.NotaEntregaDetailView.as_view(), name='nota_entrega_detail'),
    path('notas-entrega/editar/<int:pk>/', views.NotaEntregaUpdateView.as_view(), name='nota_entrega_update'),
    path('notas-entrega/eliminar/<int:pk>/', views.NotaEntregaDeleteView.as_view(), name='nota_entrega_delete'),
]
