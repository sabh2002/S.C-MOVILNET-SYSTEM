from django import forms
from .models import Marca, Proveedor, Cliente, Producto


class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ['nombre_marca', 'estado']
        widgets = {
            'nombre_marca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Samsung'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'rif', 'telefono', 'email', 'direccion', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Distribuidora XYZ'}),
            'rif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. J-1234567890'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 0414-1234567'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ej. contacto@empresa.com'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección completa'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'cedula', 'telefono', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Juan Pérez'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. V-12345678'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 0424-1234567'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección completa'}),
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['marca', 'nombre', 'descripcion_caracteristicas', 'precio', 'estado', 
                  'stock_actual', 'stock_minimo', 'stock_maximo']
        widgets = {
            'marca': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Smart 8'}),
            'descripcion_caracteristicas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 
                                                                  'placeholder': 'Características del producto'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '5'}),
            'stock_maximo': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '100'}),
        }
