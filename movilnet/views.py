from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count, Q, F

from .models import Marca, Proveedor, Cliente, Producto, PerfilEmpleado
from .forms import (
    MarcaForm, ProveedorForm, ClienteForm, ProductoForm,
    LoginForm, CambiarPasswordForm, RecuperarPasswordForm,
    NuevaPasswordForm, RegistroEmpleadoForm,
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
