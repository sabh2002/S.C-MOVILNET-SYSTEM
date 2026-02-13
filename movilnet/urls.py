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
]
