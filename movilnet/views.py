from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count, Q, F
from django.db import transaction
from django.http import JsonResponse

from .models import (
    Marca, Proveedor, Cliente, Producto, PerfilEmpleado,
    TipoInventario, MovimientoInventario,
    OrdenCompra, DetalleOrdenCompra, NotaEntrega, DetalleNotaEntrega
)
from .forms import (
    MarcaForm, ProveedorForm, ClienteForm, ProductoForm,
    LoginForm, CambiarPasswordForm, VerificarUsuarioForm,
    RecuperarPasswordForm, NuevaPasswordForm, RegistroEmpleadoForm,
    TipoInventarioForm, MovimientoInventarioForm,
    OrdenCompraForm, DetalleOrdenCompraFormSet,
    NotaEntregaForm, DetalleNotaEntregaFormSet,
    EditarEmpleadoForm,
)


# ==================== AUTENTICACIÓN ====================

def login_view(request):
    """Vista de login"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.cleaned_data['user']
        login(request, user)
        return redirect(request.GET.get('next', 'dashboard'))

    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('login')


@login_required
def cambiar_password_view(request):
    """Vista para cambiar contraseña"""
    form = CambiarPasswordForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        request.user.set_password(form.cleaned_data['password_nuevo'])
        request.user.save()
        messages.success(request, 'Contraseña cambiada exitosamente. Por favor inicia sesión de nuevo.')
        logout(request)
        return redirect('login')
    return render(request, 'auth/cambiar_password.html', {'form': form})


def verificar_usuario_view(request):
    """Paso 1 de recuperación: verificar que el usuario existe"""
    form = VerificarUsuarioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.cleaned_data['user']
        request.session['recuperar_user_id'] = user.pk
        return redirect('recuperar_preguntas')
    return render(request, 'auth/recuperar_password.html', {'form': form, 'paso': 1})


def recuperar_password_view(request):
    """Paso 2 de recuperación: responder preguntas de seguridad"""
    user_id = request.session.get('recuperar_user_id')
    if not user_id:
        messages.error(request, 'Primero debes ingresar tu nombre de usuario.')
        return redirect('recuperar_password')

    from django.contrib.auth.models import User
    user = get_object_or_404(User, pk=user_id)
    form = RecuperarPasswordForm(request.POST or None, user=user)
    if request.method == 'POST' and form.is_valid():
        return redirect('nueva_password')
    return render(request, 'auth/recuperar_preguntas.html', {
        'form': form,
        'username': user.username,
        'paso': 2
    })


def nueva_password_view(request):
    """Vista paso 2: establecer nueva contraseña tras recuperación"""
    user_id = request.session.get('recuperar_user_id')
    if not user_id:
        return redirect('recuperar_password')

    from django.contrib.auth.models import User
    user = get_object_or_404(User, pk=user_id)
    form = NuevaPasswordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user.set_password(form.cleaned_data['password_nuevo'])
        user.save()
        del request.session['recuperar_user_id']
        messages.success(request, 'Contraseña restablecida exitosamente.')
        return redirect('login')
    return render(request, 'auth/nueva_password.html', {'form': form})


@login_required
def perfil_view(request):
    """Vista del perfil del usuario autenticado"""
    try:
        perfil = request.user.perfil
    except PerfilEmpleado.DoesNotExist:
        perfil = None
    return render(request, 'auth/perfil.html', {'perfil': perfil})


class AdminRequeridoMixin(UserPassesTestMixin):
    """Mixin para restringir acciones solo a administradores"""
    def test_func(self):
        try:
            return self.request.user.perfil.rol == 'admin'
        except PerfilEmpleado.DoesNotExist:
            return self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos de administrador para realizar esta acción.')
        return redirect('dashboard')


@login_required
def registro_empleado_view(request):
    """Vista para registrar nuevos empleados (solo admin)"""
    try:
        es_admin = request.user.perfil.rol == 'admin'
    except PerfilEmpleado.DoesNotExist:
        es_admin = request.user.is_superuser

    if not es_admin:
        messages.error(request, 'No tienes permisos de administrador.')
        return redirect('dashboard')

    form = RegistroEmpleadoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, '¡Empleado registrado exitosamente!')
        return redirect('lista_empleados')
    return render(request, 'auth/registro_empleado.html', {'form': form})


@login_required
def lista_empleados_view(request):
    """Vista para listar empleados (solo admin)"""
    try:
        es_admin = request.user.perfil.rol == 'admin'
    except PerfilEmpleado.DoesNotExist:
        es_admin = request.user.is_superuser

    if not es_admin:
        messages.error(request, 'No tienes permisos de administrador.')
        return redirect('dashboard')

    empleados = PerfilEmpleado.objects.select_related('user').all()
    return render(request, 'auth/lista_empleados.html', {'empleados': empleados})


class EmpleadoDetailView(LoginRequiredMixin, AdminRequeridoMixin, DetailView):
    model = PerfilEmpleado
    template_name = 'auth/empleado_detail.html'
    context_object_name = 'empleado'


class EmpleadoUpdateView(LoginRequiredMixin, AdminRequeridoMixin, UpdateView):
    model = PerfilEmpleado
    form_class = EditarEmpleadoForm
    template_name = 'auth/editar_empleado.html'
    success_url = reverse_lazy('lista_empleados')

    def form_valid(self, form):
        messages.success(self.request, '¡Empleado actualizado exitosamente!')
        return super().form_valid(form)


class EmpleadoDeleteView(LoginRequiredMixin, AdminRequeridoMixin, DeleteView):
    model = PerfilEmpleado
    template_name = 'auth/empleado_confirm_delete.html'
    success_url = reverse_lazy('lista_empleados')

    def delete(self, request, *args, **kwargs):
        empleado_a_borrar = self.get_object()
        
        # Validar no borrarse a si mismo
        if empleado_a_borrar.user == request.user:
            messages.error(self.request, 'No puedes eliminar tu propia cuenta.')
            return redirect(self.success_url)

        # Validar al menos 1 admin.
        if empleado_a_borrar.rol == 'admin':
            admins_en_sistema = PerfilEmpleado.objects.filter(rol='admin').count()
            if admins_en_sistema <= 1:
                messages.error(self.request, 'Debe existir al menos un administrador en el sistema.')
                return redirect(self.success_url)

        # Borrar el User de Django asociado.
        user = empleado_a_borrar.user
        response = super().delete(request, *args, **kwargs)
        user.delete()
        messages.success(self.request, '¡Empleado eliminado exitosamente!')
        return response


@login_required
def empleado_toggle_activo_view(request, pk):
    try:
        es_admin = request.user.perfil.rol == 'admin'
    except PerfilEmpleado.DoesNotExist:
        es_admin = request.user.is_superuser

    if not es_admin:
        messages.error(request, 'No tienes permisos de administrador.')
        return redirect('lista_empleados')

    perfil = get_object_or_404(PerfilEmpleado, pk=pk)
    if perfil.user == request.user:
        messages.error(request, 'No puedes inactivar tu propia cuenta.')
        return redirect('lista_empleados')
        
    user = perfil.user
    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    
    estado = "activado" if user.is_active else "inactivado"
    messages.success(request, f'Empleado {estado} con éxito.')
    return redirect('lista_empleados')


# ==================== DASHBOARD ====================

@login_required
def dashboard(request):
    """Vista principal del dashboard con estadísticas"""
    context = {
        'total_productos': Producto.objects.filter(estado=True).count(),
        'total_clientes': Cliente.objects.count(),
        'total_proveedores': Proveedor.objects.filter(estado=True).count(),
        'total_marcas': Marca.objects.filter(estado=True).count(),
        'productos_bajo_stock': Producto.objects.filter(
            stock_actual__lte=F('stock_minimo')
        ).count(),
    }
    return render(request, 'dashboard_home.html', context)


# ==================== CRUD MARCA ====================

class MarcaListView(LoginRequiredMixin, ListView):
    model = Marca
    template_name = 'marcas/marca_list.html'
    context_object_name = 'marcas'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(nombre_marca__icontains=search))
        return queryset


class MarcaCreateView(LoginRequiredMixin, CreateView):
    model = Marca
    form_class = MarcaForm
    template_name = 'marcas/marca_form.html'
    success_url = reverse_lazy('marca_list')

    def form_valid(self, form):
        messages.success(self.request, '¡Marca creada exitosamente!')
        return super().form_valid(form)


class MarcaUpdateView(LoginRequiredMixin, UpdateView):
    model = Marca
    form_class = MarcaForm
    template_name = 'marcas/marca_form.html'
    success_url = reverse_lazy('marca_list')

    def form_valid(self, form):
        messages.success(self.request, '¡Marca actualizada exitosamente!')
        return super().form_valid(form)


class MarcaDeleteView(LoginRequiredMixin, AdminRequeridoMixin, DeleteView):
    model = Marca
    template_name = 'marcas/marca_confirm_delete.html'
    success_url = reverse_lazy('marca_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '¡Marca eliminada exitosamente!')
        return super().delete(request, *args, **kwargs)


@login_required
def marca_crear_ajax(request):
    """Crea una marca vía AJAX desde el modal del formulario de producto."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    form = MarcaForm(request.POST)
    if form.is_valid():
        marca = form.save()
        return JsonResponse({'success': True, 'id': marca.pk, 'nombre': marca.nombre_marca})
    return JsonResponse({'success': False, 'errors': form.errors})


# ==================== CRUD PROVEEDOR ====================

class ProveedorListView(LoginRequiredMixin, ListView):
    model = Proveedor
    template_name = 'proveedores/proveedor_list.html'
    context_object_name = 'proveedores'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(rif__icontains=search) |
                Q(email__icontains=search)
            )
        return queryset


class ProveedorCreateView(LoginRequiredMixin, CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'proveedores/proveedor_form.html'
    success_url = reverse_lazy('proveedor_list')

    def form_valid(self, form):
        messages.success(self.request, '¡Proveedor creado exitosamente!')
        return super().form_valid(form)


class ProveedorUpdateView(LoginRequiredMixin, UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'proveedores/proveedor_form.html'
    success_url = reverse_lazy('proveedor_list')

    def form_valid(self, form):
        messages.success(self.request, '¡Proveedor actualizado exitosamente!')
        return super().form_valid(form)


class ProveedorDeleteView(LoginRequiredMixin, AdminRequeridoMixin, DeleteView):
    model = Proveedor
    template_name = 'proveedores/proveedor_confirm_delete.html'
    success_url = reverse_lazy('proveedor_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '¡Proveedor eliminado exitosamente!')
        return super().delete(request, *args, **kwargs)


# ==================== CRUD CLIENTE ====================

class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'clientes/cliente_list.html'
    context_object_name = 'clientes'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(cedula__icontains=search) |
                Q(telefono__icontains=search)
            )
        return queryset


class ClienteCreateView(LoginRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('cliente_list')

    def form_valid(self, form):
        messages.success(self.request, '¡Cliente creado exitosamente!')
        return super().form_valid(form)


class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('cliente_list')

    def form_valid(self, form):
        messages.success(self.request, '¡Cliente actualizado exitosamente!')
        return super().form_valid(form)


class ClienteDeleteView(LoginRequiredMixin, AdminRequeridoMixin, DeleteView):
    model = Cliente
    template_name = 'clientes/cliente_confirm_delete.html'
    success_url = reverse_lazy('cliente_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '¡Cliente eliminado exitosamente!')
        return super().delete(request, *args, **kwargs)


# ==================== CRUD PRODUCTO ====================

class ProductoListView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = 'productos/producto_list.html'
    context_object_name = 'productos'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(marca__nombre_marca__icontains=search)
            )
        return queryset


class ProductoCreateView(LoginRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/producto_form.html'
    success_url = reverse_lazy('producto_list')

    def form_valid(self, form):
        messages.success(self.request, '¡Producto creado exitosamente!')
        return super().form_valid(form)


class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/producto_form.html'
    success_url = reverse_lazy('producto_list')

    def form_valid(self, form):
        messages.success(self.request, '¡Producto actualizado exitosamente!')
        return super().form_valid(form)


class ProductoDeleteView(LoginRequiredMixin, AdminRequeridoMixin, DeleteView):
    model = Producto
    template_name = 'productos/producto_confirm_delete.html'
    success_url = reverse_lazy('producto_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '¡Producto eliminado exitosamente!')
        return super().delete(request, *args, **kwargs)


# ==================== CRUD TIPO INVENTARIO ====================

class TipoInventarioListView(LoginRequiredMixin, ListView):
    model = TipoInventario
    template_name = 'inventario/tipo_inventario_list.html'
    context_object_name = 'tipos'
    paginate_by = 10


class TipoInventarioCreateView(LoginRequiredMixin, CreateView):
    model = TipoInventario
    form_class = TipoInventarioForm
    template_name = 'inventario/tipo_inventario_form.html'
    success_url = reverse_lazy('tipo_inventario_list')

    def form_valid(self, form):
        messages.success(self.request, '¡Tipo de inventario creado exitosamente!')
        return super().form_valid(form)


class TipoInventarioUpdateView(LoginRequiredMixin, UpdateView):
    model = TipoInventario
    form_class = TipoInventarioForm
    template_name = 'inventario/tipo_inventario_form.html'
    success_url = reverse_lazy('tipo_inventario_list')

    def form_valid(self, form):
        messages.success(self.request, '¡Tipo de inventario actualizado!')
        return super().form_valid(form)


class TipoInventarioDeleteView(LoginRequiredMixin, AdminRequeridoMixin, DeleteView):
    model = TipoInventario
    template_name = 'inventario/tipo_inventario_confirm_delete.html'
    success_url = reverse_lazy('tipo_inventario_list')


# ==================== MOVIMIENTOS DE INVENTARIO ====================

class MovimientoInventarioListView(LoginRequiredMixin, ListView):
    model = MovimientoInventario
    template_name = 'inventario/movimiento_list.html'
    context_object_name = 'movimientos'
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset().select_related('producto', 'tipo_inventario', 'empleado')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(producto__nombre__icontains=search) |
                Q(tipo_inventario__tipo_movimiento__icontains=search)
            )
        return queryset


class MovimientoInventarioCreateView(LoginRequiredMixin, CreateView):
    model = MovimientoInventario
    form_class = MovimientoInventarioForm
    template_name = 'inventario/movimiento_form.html'
    success_url = reverse_lazy('movimiento_list')

    def form_valid(self, form):
        movimiento = form.save(commit=False)
        # Asegurar que el usuario tenga perfil para registrar quién hizo el movimiento
        perfil, created = PerfilEmpleado.objects.get_or_create(
            user=self.request.user,
            defaults={
                'rol': 'admin' if self.request.user.is_superuser else 'empleado',
                'animal_favorito': '-',
                'color_favorito': '-',
            }
        )
        movimiento.empleado = perfil

        producto = movimiento.producto
        tipo = movimiento.tipo_inventario

        if tipo.es_entrada:
            producto.stock_actual += movimiento.cantidad
        else:  # SALIDA
            if producto.stock_actual >= movimiento.cantidad:
                producto.stock_actual -= movimiento.cantidad
            else:
                messages.error(
                    self.request,
                    f'Stock insuficiente para "{producto.nombre}". '
                    f'Disponible: {producto.stock_actual} unidades.'
                )
                return self.form_invalid(form)

        with transaction.atomic():
            producto.save()
            movimiento.save()

        messages.success(self.request, '¡Movimiento registrado exitosamente!')
        return redirect(self.success_url)


# ==================== STOCK ACTUAL ====================

@login_required
def stock_actual_view(request):
    """Vista de estado actual del inventario de todos los productos"""
    from django.db.models import F

    productos = Producto.objects.select_related('marca').filter(estado=True).order_by('nombre')

    # Filtro por estado de stock
    filtro_estado = request.GET.get('estado', '')
    if filtro_estado == 'sin_stock':
        productos = productos.filter(stock_actual=0)
    elif filtro_estado == 'bajo':
        productos = productos.filter(stock_actual__gt=0, stock_actual__lt=F('stock_minimo'))
    elif filtro_estado == 'normal':
        productos = productos.filter(stock_actual__gte=F('stock_minimo'), stock_actual__lt=F('stock_maximo'))
    elif filtro_estado == 'maximo':
        productos = productos.filter(stock_actual__gte=F('stock_maximo'))

    # Filtro por marca
    filtro_marca = request.GET.get('marca', '')
    if filtro_marca:
        productos = productos.filter(marca__id=filtro_marca)

    marcas = Marca.objects.filter(estado=True).order_by('nombre_marca')

    context = {
        'productos': productos,
        'marcas': marcas,
        'filtro_estado': filtro_estado,
        'filtro_marca': filtro_marca,
        'total_productos': productos.count(),
        'sin_stock': Producto.objects.filter(estado=True, stock_actual=0).count(),
        'stock_bajo': Producto.objects.filter(
            estado=True, stock_actual__gt=0, stock_actual__lt=F('stock_minimo')
        ).count(),
    }
    return render(request, 'inventario/stock_actual.html', context)


# ==================== CRUD ORDEN DE COMPRA / COMPRA ====================

class OrdenCompraListView(LoginRequiredMixin, AdminRequeridoMixin, ListView):
    model = OrdenCompra
    template_name = 'ordenes/orden_compra_list.html'
    context_object_name = 'ordenes'
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().select_related('proveedor')


class OrdenCompraDetailView(LoginRequiredMixin, AdminRequeridoMixin, DetailView):
    model = OrdenCompra
    template_name = 'ordenes/orden_compra_detail.html'
    context_object_name = 'orden'


class OrdenCompraCreateView(LoginRequiredMixin, AdminRequeridoMixin, CreateView):
    model = OrdenCompra
    form_class = OrdenCompraForm
    template_name = 'ordenes/orden_compra_form.html'
    success_url = reverse_lazy('orden_compra_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detalles'] = DetalleOrdenCompraFormSet(self.request.POST)
        else:
            context['detalles'] = DetalleOrdenCompraFormSet()
        context['productos_disponibles'] = Producto.objects.filter(estado=True).select_related('marca').order_by('nombre')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        if not detalles.is_valid():
            messages.error(self.request, 'Corrige los errores en los productos.')
            return self.form_invalid(form)
        with transaction.atomic():
            self.object = form.save()
            detalles.instance = self.object
            detalles.save()
            # Calcular total
            self.object.total = sum(d.subtotal for d in self.object.detalles.all())
            self.object.save(update_fields=['total'])
            # Solo "Compra" actualiza el stock (mercancía ya recibida)
            if self.object.tipo == 'compra':
                for detalle in self.object.detalles.all():
                    detalle.producto.stock_actual += detalle.cantidad
                    detalle.producto.save(update_fields=['stock_actual'])
        tipo_label = 'Compra' if self.object.tipo == 'compra' else 'Orden de compra'
        messages.success(self.request, f'¡{tipo_label} registrada exitosamente!')
        return redirect(self.success_url)


class OrdenCompraUpdateView(LoginRequiredMixin, AdminRequeridoMixin, UpdateView):
    model = OrdenCompra
    form_class = OrdenCompraForm
    template_name = 'ordenes/orden_compra_form.html'
    success_url = reverse_lazy('orden_compra_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detalles'] = DetalleOrdenCompraFormSet(self.request.POST, instance=self.object)
        else:
            context['detalles'] = DetalleOrdenCompraFormSet(instance=self.object)
        context['productos_disponibles'] = Producto.objects.filter(estado=True).select_related('marca').order_by('nombre')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        if not detalles.is_valid():
            messages.error(self.request, 'Corrige los errores en los productos.')
            return self.form_invalid(form)

        tipo_previo = self.object.tipo
        # Si era Compra, devolver el stock antes de recalcular
        cantidades_previas = {}
        if tipo_previo == 'compra':
            for d in self.object.detalles.all():
                cantidades_previas[d.pk] = {'cantidad': d.cantidad, 'producto': d.producto}

        with transaction.atomic():
            if tipo_previo == 'compra':
                for pk, info in cantidades_previas.items():
                    info['producto'].stock_actual -= info['cantidad']
                    info['producto'].save(update_fields=['stock_actual'])

            self.object = form.save()
            detalles.instance = self.object
            detalles.save()

            self.object.total = sum(d.subtotal for d in self.object.detalles.all())
            self.object.save(update_fields=['total'])

            if self.object.tipo == 'compra':
                for detalle in self.object.detalles.all():
                    detalle.producto.refresh_from_db()
                    detalle.producto.stock_actual += detalle.cantidad
                    detalle.producto.save(update_fields=['stock_actual'])

        messages.success(self.request, '¡Registro actualizado exitosamente!')
        return redirect(self.success_url)


class OrdenCompraDeleteView(LoginRequiredMixin, AdminRequeridoMixin, DeleteView):
    model = OrdenCompra
    template_name = 'ordenes/orden_compra_confirm_delete.html'
    success_url = reverse_lazy('orden_compra_list')

    def delete(self, request, *args, **kwargs):
        orden = self.get_object()
        with transaction.atomic():
            # Si era Compra, devolver el stock al eliminar
            if orden.tipo == 'compra':
                for detalle in orden.detalles.all():
                    detalle.producto.stock_actual -= detalle.cantidad
                    detalle.producto.save(update_fields=['stock_actual'])
            orden.delete()
        messages.success(request, '¡Registro eliminado exitosamente!')
        return redirect(self.success_url)


# ==================== CRUD NOTA DE ENTREGA ====================

class NotaEntregaListView(LoginRequiredMixin, ListView):
    model = NotaEntrega
    template_name = 'notas_entrega/nota_entrega_list.html'
    context_object_name = 'notas'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('cliente')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(cliente__nombre__icontains=search) |
                Q(numero_entrega__icontains=search)
            )
        return queryset


class NotaEntregaDetailView(LoginRequiredMixin, DetailView):
    model = NotaEntrega
    template_name = 'notas_entrega/nota_entrega_detail.html'
    context_object_name = 'nota'


class NotaEntregaCreateView(LoginRequiredMixin, CreateView):
    model = NotaEntrega
    form_class = NotaEntregaForm
    template_name = 'notas_entrega/nota_entrega_form.html'
    success_url = reverse_lazy('nota_entrega_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detalles'] = DetalleNotaEntregaFormSet(self.request.POST)
        else:
            context['detalles'] = DetalleNotaEntregaFormSet()
        context['productos'] = Producto.objects.filter(estado=True).select_related('marca').order_by('nombre')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        if not detalles.is_valid():
            messages.error(self.request, 'Corrige los errores en los detalles de la nota.')
            return self.form_invalid(form)

        # Validar stock disponible ANTES de guardar
        for detalle_form in detalles:
            if detalle_form.cleaned_data and not detalle_form.cleaned_data.get('DELETE', False):
                producto = detalle_form.cleaned_data['producto']
                cantidad = detalle_form.cleaned_data['cantidad']
                descuento = detalle_form.cleaned_data.get('descuento', 0)
                precio = detalle_form.cleaned_data.get('precio_unitario', 0)

                if cantidad > producto.stock_actual:
                    messages.error(
                        self.request,
                        f'Stock insuficiente para "{producto.nombre}". '
                        f'Solicitado: {cantidad}, Disponible: {producto.stock_actual}.'
                    )
                    return self.form_invalid(form)

                # Validar que el descuento no supere el valor de la línea
                valor_linea = cantidad * precio
                if descuento > valor_linea:
                    messages.error(
                        self.request,
                        f'El descuento (${descuento}) no puede superar el valor '
                        f'de la línea (${valor_linea}) para "{producto.nombre}".'
                    )
                    return self.form_invalid(form)

        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.save()
            detalles.instance = self.object
            detalles.save()

            # Calcular subtotales por línea, descontar stock y calcular totales
            subtotal_general = 0
            for d in self.object.detalles.all():
                # Calcular y guardar subtotal de la línea
                d.subtotal = d.cantidad * d.precio_unitario - d.descuento
                d.save(update_fields=['subtotal'])
                subtotal_general += d.subtotal

                # DESCONTAR STOCK
                d.producto.stock_actual -= d.cantidad
                d.producto.save(update_fields=['stock_actual'])

            self.object.subtotal = subtotal_general
            self.object.total = subtotal_general - self.object.descuento
            self.object.save(update_fields=['subtotal', 'total'])

        messages.success(self.request, '¡Nota de entrega creada exitosamente!')
        return redirect(self.success_url)


class NotaEntregaUpdateView(LoginRequiredMixin, UpdateView):
    model = NotaEntrega
    form_class = NotaEntregaForm
    template_name = 'notas_entrega/nota_entrega_form.html'
    success_url = reverse_lazy('nota_entrega_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detalles'] = DetalleNotaEntregaFormSet(self.request.POST, instance=self.object)
        else:
            context['detalles'] = DetalleNotaEntregaFormSet(instance=self.object)
        context['productos'] = Producto.objects.filter(estado=True).select_related('marca').order_by('nombre')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        if not detalles.is_valid():
            messages.error(self.request, 'Corrige los errores en los detalles de la nota.')
            return self.form_invalid(form)

        # Guardar cantidades previas para calcular diferencia de stock
        cantidades_previas = {}
        for d in self.object.detalles.all():
            cantidades_previas[d.pk] = {'cantidad': d.cantidad, 'producto_id': d.producto_id}

        # Validar stock para las nuevas cantidades
        for detalle_form in detalles:
            if detalle_form.cleaned_data and not detalle_form.cleaned_data.get('DELETE', False):
                producto = detalle_form.cleaned_data['producto']
                cantidad_nueva = detalle_form.cleaned_data['cantidad']
                descuento = detalle_form.cleaned_data.get('descuento', 0)
                precio = detalle_form.cleaned_data.get('precio_unitario', 0)

                # Calcular stock disponible considerando devolución de la cantidad previa
                detalle_pk = detalle_form.instance.pk
                cantidad_previa = cantidades_previas.get(detalle_pk, {}).get('cantidad', 0)
                stock_disponible = producto.stock_actual + cantidad_previa

                if cantidad_nueva > stock_disponible:
                    messages.error(
                        self.request,
                        f'Stock insuficiente para "{producto.nombre}". '
                        f'Disponible: {stock_disponible}.'
                    )
                    return self.form_invalid(form)

                valor_linea = cantidad_nueva * precio
                if descuento > valor_linea:
                    messages.error(
                        self.request,
                        f'El descuento (${descuento}) supera el valor de la línea '
                        f'(${valor_linea}) para "{producto.nombre}".'
                    )
                    return self.form_invalid(form)

        with transaction.atomic():
            # Devolver stock de las líneas previas
            for d in self.object.detalles.all():
                d.producto.stock_actual += d.cantidad
                d.producto.save(update_fields=['stock_actual'])

            self.object = form.save()
            detalles.instance = self.object
            detalles.save()

            # Recalcular subtotales y descontar stock nuevo
            subtotal_general = 0
            for d in self.object.detalles.all():
                d.subtotal = d.cantidad * d.precio_unitario - d.descuento
                d.save(update_fields=['subtotal'])
                subtotal_general += d.subtotal

                # Descontar stock actualizado
                d.producto.refresh_from_db()
                d.producto.stock_actual -= d.cantidad
                d.producto.save(update_fields=['stock_actual'])

            self.object.subtotal = subtotal_general
            self.object.total = subtotal_general - self.object.descuento
            self.object.save(update_fields=['subtotal', 'total'])

        messages.success(self.request, '¡Nota de entrega actualizada!')
        return redirect(self.success_url)


class NotaEntregaDeleteView(LoginRequiredMixin, AdminRequeridoMixin, DeleteView):
    model = NotaEntrega
    template_name = 'notas_entrega/nota_entrega_confirm_delete.html'
    success_url = reverse_lazy('nota_entrega_list')

    def delete(self, request, *args, **kwargs):
        nota = self.get_object()
        # Devolver stock de todos los productos de esta nota antes de eliminar
        with transaction.atomic():
            for detalle in nota.detalles.all():
                detalle.producto.stock_actual += detalle.cantidad
                detalle.producto.save(update_fields=['stock_actual'])
            nota.delete()
        messages.success(request, '¡Nota de entrega eliminada y stock devuelto!')
        return redirect(self.success_url)


# ==================== REPORTES ====================

@login_required
def reporte_inventario_view(request):
    """Reporte imprimible de inventario actual"""
    from django.db.models import F, Sum, ExpressionWrapper, DecimalField

    productos = Producto.objects.select_related('marca').filter(estado=True).order_by('marca__nombre_marca', 'nombre')

    # Filtro por marca
    filtro_marca = request.GET.get('marca', '')
    if filtro_marca:
        productos = productos.filter(marca__id=filtro_marca)

    # Filtro por estado de stock
    filtro_estado = request.GET.get('estado', '')
    if filtro_estado == 'sin_stock':
        productos = productos.filter(stock_actual=0)
    elif filtro_estado == 'bajo':
        productos = productos.filter(stock_actual__gt=0, stock_actual__lt=F('stock_minimo'))
    elif filtro_estado == 'normal':
        productos = productos.filter(stock_actual__gte=F('stock_minimo'), stock_actual__lt=F('stock_maximo'))

    # Calcular valor total del inventario
    valor_total = productos.aggregate(
        total=Sum(
            ExpressionWrapper(
                F('stock_actual') * F('precio'),
                output_field=DecimalField()
            )
        )
    )['total'] or 0

    total_unidades = productos.aggregate(total=Sum('stock_actual'))['total'] or 0

    marcas = Marca.objects.filter(estado=True).order_by('nombre_marca')

    context = {
        'productos': productos,
        'marcas': marcas,
        'filtro_marca': filtro_marca,
        'filtro_estado': filtro_estado,
        'total_productos': productos.count(),
        'total_unidades': total_unidades,
        'valor_total': valor_total,
    }
    return render(request, 'reportes/reporte_inventario.html', context)


@login_required
def reporte_movimientos_view(request):
    """Reporte de movimientos de inventario por rango de fecha"""
    from django.db.models import Sum
    from datetime import date, timedelta

    movimientos = MovimientoInventario.objects.select_related(
        'producto', 'tipo_inventario', 'empleado__user'
    ).order_by('-fecha_movimiento')

    # Filtros de fecha
    fecha_desde = request.GET.get('desde', '')
    fecha_hasta = request.GET.get('hasta', '')

    if fecha_desde:
        movimientos = movimientos.filter(fecha_movimiento__date__gte=fecha_desde)
    if fecha_hasta:
        movimientos = movimientos.filter(fecha_movimiento__date__lte=fecha_hasta)

    # Filtro por dirección
    filtro_direccion = request.GET.get('direccion', '')
    if filtro_direccion in ('ENTRADA', 'SALIDA'):
        movimientos = movimientos.filter(tipo_inventario__direccion=filtro_direccion)

    # Filtro por producto
    filtro_producto = request.GET.get('producto', '')
    if filtro_producto:
        movimientos = movimientos.filter(producto__id=filtro_producto)

    # Calcular totales
    entradas = movimientos.filter(tipo_inventario__direccion='ENTRADA')
    salidas = movimientos.filter(tipo_inventario__direccion='SALIDA')
    total_entradas = entradas.aggregate(t=Sum('cantidad'))['t'] or 0
    total_salidas = salidas.aggregate(t=Sum('cantidad'))['t'] or 0

    productos = Producto.objects.filter(estado=True).order_by('nombre')

    context = {
        'movimientos': movimientos[:200],  # Limitar para rendimiento
        'productos': productos,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'filtro_direccion': filtro_direccion,
        'filtro_producto': filtro_producto,
        'total_movimientos': movimientos.count(),
        'total_entradas': total_entradas,
        'total_salidas': total_salidas,
        'balance_neto': total_entradas - total_salidas,
    }
    return render(request, 'reportes/reporte_movimientos.html', context)


@login_required
def reporte_ventas_view(request):
    """Reporte de ventas (notas de entrega) por periodo"""
    from django.db.models import Sum, Count
    from datetime import date

    notas = NotaEntrega.objects.select_related('cliente').prefetch_related('detalles__producto').order_by('-fecha_registro')

    # Filtros de fecha
    fecha_desde = request.GET.get('desde', '')
    fecha_hasta = request.GET.get('hasta', '')

    if fecha_desde:
        notas = notas.filter(fecha_registro__date__gte=fecha_desde)
    if fecha_hasta:
        notas = notas.filter(fecha_registro__date__lte=fecha_hasta)

    # Filtro por cliente
    filtro_cliente = request.GET.get('cliente', '')
    if filtro_cliente:
        notas = notas.filter(cliente__id=filtro_cliente)

    # Totales
    totales = notas.aggregate(
        subtotal_total=Sum('subtotal'),
        descuento_total=Sum('descuento'),
        total_total=Sum('total'),
    )

    clientes = Cliente.objects.order_by('nombre')

    context = {
        'notas': notas[:200],
        'clientes': clientes,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'filtro_cliente': filtro_cliente,
        'total_notas': notas.count(),
        'subtotal_total': totales['subtotal_total'] or 0,
        'descuento_total': totales['descuento_total'] or 0,
        'total_total': totales['total_total'] or 0,
    }
    return render(request, 'reportes/reporte_ventas.html', context)
