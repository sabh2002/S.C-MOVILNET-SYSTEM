from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count, Q, F
from django.core.paginator import Paginator

from .models import Marca, Proveedor, Cliente, Producto
from .forms import MarcaForm, ProveedorForm, ClienteForm, ProductoForm


# Vista Dashboard
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

class MarcaListView(ListView):
    model = Marca
    template_name = 'marcas/marca_list.html'
    context_object_name = 'marcas'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombre_marca__icontains=search)
            )
        return queryset


class MarcaCreateView(CreateView):
    model = Marca
    form_class = MarcaForm
    template_name = 'marcas/marca_form.html'
    success_url = reverse_lazy('marca_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'ยกMarca creada exitosamente!')
        return super().form_valid(form)


class MarcaUpdateView(UpdateView):
    model = Marca
    form_class = MarcaForm
    template_name = 'marcas/marca_form.html'
    success_url = reverse_lazy('marca_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'ยกMarca actualizada exitosamente!')
        return super().form_valid(form)


class MarcaDeleteView(DeleteView):
    model = Marca
    template_name = 'marcas/marca_confirm_delete.html'
    success_url = reverse_lazy('marca_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'ยกMarca eliminada exitosamente!')
        return super().delete(request, *args, **kwargs)


# ==================== CRUD PROVEEDOR ====================

class ProveedorListView(ListView):
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


class ProveedorCreateView(CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'proveedores/proveedor_form.html'
    success_url = reverse_lazy('proveedor_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'ยกProveedor creado exitosamente!')
        return super().form_valid(form)


class ProveedorUpdateView(UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'proveedores/proveedor_form.html'
    success_url = reverse_lazy('proveedor_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'ยกProveedor actualizado exitosamente!')
        return super().form_valid(form)


class ProveedorDeleteView(DeleteView):
    model = Proveedor
    template_name = 'proveedores/proveedor_confirm_delete.html'
    success_url = reverse_lazy('proveedor_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'ยกProveedor eliminado exitosamente!')
        return super().delete(request, *args, **kwargs)


# ==================== CRUD CLIENTE ====================

class ClienteListView(ListView):
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


class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('cliente_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'ยกCliente creado exitosamente!')
        return super().form_valid(form)


class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('cliente_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'ยกCliente actualizado exitosamente!')
        return super().form_valid(form)


class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = 'clientes/cliente_confirm_delete.html'
    success_url = reverse_lazy('cliente_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'ยกCliente eliminado exitosamente!')
        return super().delete(request, *args, **kwargs)


# ==================== CRUD PRODUCTO ====================

class ProductoListView(ListView):
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


class ProductoCreateView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/producto_form.html'
    success_url = reverse_lazy('producto_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'ยกProducto creado exitosamente!')
        return super().form_valid(form)


class ProductoUpdateView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/producto_form.html'
    success_url = reverse_lazy('producto_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'ยกProducto actualizado exitosamente!')
        return super().form_valid(form)


class ProductoDeleteView(DeleteView):
    model = Producto
    template_name = 'productos/producto_confirm_delete.html'
    success_url = reverse_lazy('producto_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'ยกProducto eliminado exitosamente!')
        return super().delete(request, *args, **kwargs)
