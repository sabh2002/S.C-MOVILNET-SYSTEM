from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Marca, Proveedor, Cliente, Producto, PerfilEmpleado


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
    TIPO_CEDULA_CHOICES = [
        ('V', 'V - Venezolano'),
        ('E', 'E - Extranjero'),
        ('J', 'J - Jurídico'),
        ('P', 'P - Pasaporte'),
        ('G', 'G - Gobierno'),
    ]

    tipo_cedula = forms.ChoiceField(
        choices=TIPO_CEDULA_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Tipo'
    )
    numero_cedula = forms.CharField(
        max_length=8,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej. 12345678',
            'maxlength': '8'
        }),
        label='Número de Cédula'
    )

    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Juan Pérez'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 0424-1234567'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección completa'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.cedula:
            cedula_parts = self.instance.cedula.split('-')
            if len(cedula_parts) == 2:
                self.fields['tipo_cedula'].initial = cedula_parts[0]
                self.fields['numero_cedula'].initial = cedula_parts[1]

    def clean_numero_cedula(self):
        numero = self.cleaned_data.get('numero_cedula', '')
        if not numero.isdigit():
            raise forms.ValidationError('El número de cédula debe contener solo dígitos.')
        if len(numero) < 6 or len(numero) > 8:
            raise forms.ValidationError('El número de cédula debe tener entre 6 y 8 dígitos.')
        return numero

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo_cedula')
        numero = cleaned_data.get('numero_cedula')

        if tipo and numero:
            cedula_completa = f"{tipo}-{numero}"
            cleaned_data['cedula'] = cedula_completa

            existing = Cliente.objects.filter(cedula=cedula_completa)
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError({'numero_cedula': 'Ya existe un cliente con esta cédula.'})

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.cedula = self.cleaned_data.get('cedula')
        if commit:
            instance.save()
        return instance


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


# ==================== FORMULARIOS DE AUTENTICACIÓN ====================

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError('Usuario o contraseña incorrectos.')
            if not user.is_active:
                raise forms.ValidationError('Esta cuenta está desactivada.')
            cleaned_data['user'] = user
        return cleaned_data


class CambiarPasswordForm(forms.Form):
    password_actual = forms.CharField(
        label='Contraseña actual',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña actual'})
    )
    password_nuevo = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nueva contraseña'})
    )
    password_confirmar = forms.CharField(
        label='Confirmar nueva contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repita la nueva contraseña'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_password_actual(self):
        password = self.cleaned_data.get('password_actual')
        if self.user and not self.user.check_password(password):
            raise forms.ValidationError('La contraseña actual es incorrecta.')
        return password

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password_nuevo')
        p2 = cleaned_data.get('password_confirmar')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError({'password_confirmar': 'Las contraseñas no coinciden.'})
        return cleaned_data


class RecuperarPasswordForm(forms.Form):
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'})
    )
    animal_favorito = forms.CharField(
        label='¿Cuál es tu animal favorito?',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Animal favorito'})
    )
    color_favorito = forms.CharField(
        label='¿Cuál es tu color favorito?',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Color favorito'})
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        animal = cleaned_data.get('animal_favorito', '').strip().lower()
        color = cleaned_data.get('color_favorito', '').strip().lower()
        if username:
            try:
                user = User.objects.get(username=username)
                perfil = user.perfil
                if perfil.animal_favorito.strip().lower() != animal or \
                   perfil.color_favorito.strip().lower() != color:
                    raise forms.ValidationError('Las respuestas de seguridad no coinciden.')
                cleaned_data['user'] = user
            except User.DoesNotExist:
                raise forms.ValidationError('El usuario no existe.')
            except PerfilEmpleado.DoesNotExist:
                raise forms.ValidationError('Este usuario no tiene perfil de empleado.')
        return cleaned_data


class NuevaPasswordForm(forms.Form):
    password_nuevo = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nueva contraseña'})
    )
    password_confirmar = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repita la contraseña'})
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password_nuevo')
        p2 = cleaned_data.get('password_confirmar')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError({'password_confirmar': 'Las contraseñas no coinciden.'})
        return cleaned_data


class RegistroEmpleadoForm(forms.ModelForm):
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'})
    )
    first_name = forms.CharField(
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )
    last_name = forms.CharField(
        label='Apellido',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )
    password_confirmar = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repita la contraseña'})
    )

    class Meta:
        model = PerfilEmpleado
        fields = ['rol', 'animal_favorito', 'color_favorito']
        widgets = {
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'animal_favorito': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Perro'}),
            'color_favorito': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Azul'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Ese nombre de usuario ya está en uso.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirmar')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError({'password_confirmar': 'Las contraseñas no coinciden.'})
        return cleaned_data

    def save(self, commit=True):
        perfil = super().save(commit=False)
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            password=self.cleaned_data['password'],
        )
        perfil.user = user
        if commit:
            perfil.save()
        return perfil
