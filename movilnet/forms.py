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
    TIPO_RIF_CHOICES = [
        ('V', 'V - Venezolano'),
        ('E', 'E - Extranjero'),
        ('J', 'J - Jurídico'),
        ('P', 'P - Pasaporte'),
        ('G', 'G - Gobierno'),
    ]

    tipo_rif = forms.ChoiceField(
        choices=TIPO_RIF_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Tipo'
    )
    numero_rif = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej. 1234567890',
            'maxlength': '10'
        }),
        label='Número RIF'
    )

    class Meta:
        model = Proveedor
        fields = ['nombre', 'telefono', 'email', 'direccion', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Distribuidora XYZ'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 0414-1234567'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ej. contacto@empresa.com'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección completa'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si estamos editando un proveedor existente, separar el RIF
        if self.instance and self.instance.pk and self.instance.rif:
            rif_parts = self.instance.rif.split('-')
            if len(rif_parts) == 2:
                self.fields['tipo_rif'].initial = rif_parts[0]
                self.fields['numero_rif'].initial = rif_parts[1]

    def clean_numero_rif(self):
        numero = self.cleaned_data.get('numero_rif', '')
        if not numero.isdigit():
            raise forms.ValidationError('El número de RIF debe contener solo dígitos.')
        if len(numero) != 10:
            raise forms.ValidationError('El número de RIF debe tener exactamente 10 dígitos.')
        return numero

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo_rif')
        numero = cleaned_data.get('numero_rif')

        if tipo and numero:
            # Combinar tipo y número para formar el RIF completo
            rif_completo = f"{tipo}-{numero}"
            cleaned_data['rif'] = rif_completo

            # Verificar unicidad del RIF
            existing = Proveedor.objects.filter(rif=rif_completo)
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError({'numero_rif': 'Ya existe un proveedor con este RIF.'})

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Asignar el RIF combinado al modelo
        instance.rif = self.cleaned_data.get('rif')
        if commit:
            instance.save()
        return instance


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
