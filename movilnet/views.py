from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count, Q, F
from django.db import transaction

from .models import (
    Marca, Proveedor, Cliente, Producto, PerfilEmpleado,
    TipoInventario, MovimientoInventario, Cotizacion, DetalleCotizacion,
    OrdenCompra, DetalleOrdenCompra, NotaEntrega, DetalleNotaEntrega
)
from .forms import (
    MarcaForm, ProveedorForm, ClienteForm, ProductoForm,
    LoginForm, CambiarPasswordForm, RecuperarPasswordForm,
    NuevaPasswordForm, RegistroEmpleadoForm,
    TipoInventarioForm, MovimientoInventarioForm,
    CotizacionForm, DetalleCotizacionFormSet,
    OrdenCompraForm, DetalleOrdenCompraFormSet,
    NotaEntregaForm, DetalleNotaEntregaFormSet,
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


def recuperar_password_view(request):
    """Vista paso 1: verificar identidad con preguntas de seguridad"""
    form = RecuperarPasswordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        request.session['recuperar_user_id'] = form.cleaned_data['user'].pk
        return redirect('nueva_password')
    return render(request, 'auth/recuperar_password.html', {'form': form})


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
        try:
            movimiento.empleado = self.request.user.perfil
        except PerfilEmpleado.DoesNotExist:
            movimiento.empleado = None

        # Actualizar stock del producto según el tipo de movimiento
        producto = movimiento.producto
        tipo = movimiento.tipo_inventario.tipo_movimiento.lower()

        if 'entrada' in tipo or 'compra' in tipo:
            producto.stock_actual += movimiento.cantidad
        elif 'salida' in tipo or 'venta' in tipo:
            if producto.stock_actual >= movimiento.cantidad:
                producto.stock_actual -= movimiento.cantidad
            else:
                messages.error(self.request, f'Stock insuficiente. Disponible: {producto.stock_actual}')
                return self.form_invalid(form)

        producto.save()
        movimiento.save()
        messages.success(self.request, '¡Movimiento registrado exitosamente!')
        return redirect(self.success_url)


# ==================== CRUD COTIZACIÓN ====================

class CotizacionListView(LoginRequiredMixin, ListView):
    model = Cotizacion
    template_name = 'cotizaciones/cotizacion_list.html'
    context_object_name = 'cotizaciones'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('proveedor')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(proveedor__nombre__icontains=search) |
                Q(proveedor__rif__icontains=search)
            )
        return queryset


class CotizacionDetailView(LoginRequiredMixin, DetailView):
    model = Cotizacion
    template_name = 'cotizaciones/cotizacion_detail.html'
    context_object_name = 'cotizacion'


class CotizacionCreateView(LoginRequiredMixin, CreateView):
    model = Cotizacion
    form_class = CotizacionForm
    template_name = 'cotizaciones/cotizacion_form.html'
    success_url = reverse_lazy('cotizacion_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detalles'] = DetalleCotizacionFormSet(self.request.POST)
        else:
            context['detalles'] = DetalleCotizacionFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        with transaction.atomic():
            self.object = form.save()
            if detalles.is_valid():
                detalles.instance = self.object
                detalles.save()
        messages.success(self.request, '¡Cotización creada exitosamente!')
        return redirect(self.success_url)


class CotizacionUpdateView(LoginRequiredMixin, UpdateView):
    model = Cotizacion
    form_class = CotizacionForm
    template_name = 'cotizaciones/cotizacion_form.html'
    success_url = reverse_lazy('cotizacion_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detalles'] = DetalleCotizacionFormSet(self.request.POST, instance=self.object)
        else:
            context['detalles'] = DetalleCotizacionFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        with transaction.atomic():
            self.object = form.save()
            if detalles.is_valid():
                detalles.instance = self.object
                detalles.save()
        messages.success(self.request, '¡Cotización actualizada exitosamente!')
        return redirect(self.success_url)


class CotizacionDeleteView(LoginRequiredMixin, AdminRequeridoMixin, DeleteView):
    model = Cotizacion
    template_name = 'cotizaciones/cotizacion_confirm_delete.html'
    success_url = reverse_lazy('cotizacion_list')


# ==================== CRUD ORDEN DE COMPRA ====================

class OrdenCompraListView(LoginRequiredMixin, ListView):
    model = OrdenCompra
    template_name = 'ordenes/orden_compra_list.html'
    context_object_name = 'ordenes'
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().select_related('cotizacion__proveedor')


class OrdenCompraDetailView(LoginRequiredMixin, DetailView):
    model = OrdenCompra
    template_name = 'ordenes/orden_compra_detail.html'
    context_object_name = 'orden'


class OrdenCompraCreateView(LoginRequiredMixin, CreateView):
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
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        with transaction.atomic():
            self.object = form.save()
            if detalles.is_valid():
                detalles.instance = self.object
                detalles.save()
        messages.success(self.request, '¡Orden de compra creada exitosamente!')
        return redirect(self.success_url)


class OrdenCompraUpdateView(LoginRequiredMixin, UpdateView):
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
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        with transaction.atomic():
            self.object = form.save()
            if detalles.is_valid():
                detalles.instance = self.object
                detalles.save()
        messages.success(self.request, '¡Orden de compra actualizada!')
        return redirect(self.success_url)


class OrdenCompraDeleteView(LoginRequiredMixin, AdminRequeridoMixin, DeleteView):
    model = OrdenCompra
    template_name = 'ordenes/orden_compra_confirm_delete.html'
    success_url = reverse_lazy('orden_compra_list')


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
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.save()

            if detalles.is_valid():
                detalles.instance = self.object
                detalles.save()

                # Calcular totales
                subtotal = sum(
                    (d.cantidad * d.precio_unitario - d.descuento)
                    for d in self.object.detalles.all()
                )
                self.object.subtotal = subtotal
                self.object.total = subtotal - self.object.descuento
                self.object.save()

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
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        with transaction.atomic():
            self.object = form.save()
            if detalles.is_valid():
                detalles.instance = self.object
                detalles.save()

                subtotal = sum(
                    (d.cantidad * d.precio_unitario - d.descuento)
                    for d in self.object.detalles.all()
                )
                self.object.subtotal = subtotal
                self.object.total = subtotal - self.object.descuento
                self.object.save()

        messages.success(self.request, '¡Nota de entrega actualizada!')
        return redirect(self.success_url)


class NotaEntregaDeleteView(LoginRequiredMixin, AdminRequeridoMixin, DeleteView):
    model = NotaEntrega
    template_name = 'notas_entrega/nota_entrega_confirm_delete.html'
    success_url = reverse_lazy('nota_entrega_list')
