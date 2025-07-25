from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from .models import Usuario, Rol
import re

class RegistroTutorForm(forms.ModelForm):
    confirmar_contraseña = forms.CharField(
        widget=forms.PasswordInput(), 
        label="Confirmar contraseña"
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido_materno', 'apellido_paterno', 'curp', 'correo', 'telefono', 'contraseña_hash']
        widgets = {
            'contraseña_hash': forms.PasswordInput(attrs={'placeholder': 'Contraseña'}),
        }
        labels = {
            'nombre': 'Nombre',
            'apellido_materno': 'Apellido materno',
            'apellido_paterno': 'Apellido paterno',
            'curp': 'CURP',
            'correo': 'Correo electrónico',
            'telefono': 'Teléfono',
            'contraseña_hash': 'Contraseña',
        }

    # Validar campos individuales:
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if not nombre.replace(" ", "").isalpha():
            raise ValidationError("El nombre solo debe contener letras.")
        return nombre

    def clean_apellido_materno(self):
        apellido = self.cleaned_data['apellido_materno']
        if not apellido.replace(" ", "").isalpha():
            raise ValidationError("El apellido materno solo debe contener letras.")
        return apellido

    def clean_apellido_paterno(self):
        apellido = self.cleaned_data['apellido_paterno']
        if not apellido.replace(" ", "").isalpha():
            raise ValidationError("El apellido paterno solo debe contener letras.")
        return apellido

    def clean_curp(self):
        curp = self.cleaned_data['curp']
        if len(curp) != 18:
            raise ValidationError("La CURP debe tener exactamente 18 caracteres.")
        return curp.upper()

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        if not telefono.isdigit() or len(telefono) != 10:
            raise ValidationError("El teléfono debe contener exactamente 10 números.")
        return telefono

    def clean_contraseña_hash(self):
        contraseña = self.cleaned_data['contraseña_hash']
        if len(contraseña) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r"[A-Za-z]", contraseña):
            raise ValidationError("La contraseña debe contener al menos una letra.")
        if not re.search(r"[0-9]", contraseña):
            raise ValidationError("La contraseña debe contener al menos un número.")
        if not re.search(r"[!@#$%^&*()_+{}\[\]:;<>,.?~\\-]", contraseña):
            raise ValidationError("La contraseña debe contener al menos un carácter especial.")
        return contraseña

    # Validación general: confirmar contraseña
    def clean(self):
        cleaned_data = super().clean()
        contraseña = cleaned_data.get("contraseña_hash")
        confirmar = cleaned_data.get("confirmar_contraseña")
        if contraseña and confirmar and contraseña != confirmar:
            self.add_error('confirmar_contraseña', "Las contraseñas no coinciden.")

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.contraseña_hash = make_password(self.cleaned_data["contraseña_hash"])
        if commit:
            usuario.save()
        return usuario

class LoginForm(forms.Form):
    correo = forms.CharField(label="Correo", max_length=18)
    contraseña = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

class LoginAdminForm(forms.Form):
    correo = forms.CharField(label="Correo", max_length=100)
    contraseña = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    rol = forms.TypedChoiceField(
        choices=[],
        coerce=int,
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        roles = Rol.objects.filter(nombre__in=['Profesor', 'Directivo'])
        self.fields['rol'].choices = [(rol.id, rol.nombre) for rol in roles]
        if roles.exists():
            self.initial['rol'] = roles[0].id 

class RegistroAdminForm(forms.ModelForm):
    confirmar_contraseña = forms.CharField(
        widget=forms.PasswordInput(),
        label="Confirmar contraseña"
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido_materno', 'apellido_paterno', 'curp', 'correo', 'telefono', 'contraseña_hash']
        widgets = {
            'contraseña_hash': forms.PasswordInput(attrs={'placeholder': 'Contraseña'}),
        }
        labels = {
            'nombre': 'Nombre',
            'apellido_materno': 'Apellido materno',
            'apellido_paterno': 'Apellido paterno',
            'curp': 'CURP',
            'correo': 'Correo electrónico',
            'telefono': 'Teléfono',
            'contraseña_hash': 'Contraseña',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        rol_admin = Rol.objects.get(nombre='Directivo')
        self.fields['rol_id'] = forms.ModelChoiceField(
            queryset=Rol.objects.filter(id=rol_admin.id),
            widget=forms.HiddenInput(),
            initial=rol_admin
        )

    # Validaciones individuales
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if not nombre.replace(" ", "").isalpha():
            raise ValidationError("El nombre solo debe contener letras.")
        return nombre

    def clean_apellido_materno(self):
        apellido = self.cleaned_data['apellido_materno']
        if not apellido.replace(" ", "").isalpha():
            raise ValidationError("El apellido materno solo debe contener letras.")
        return apellido

    def clean_apellido_paterno(self):
        apellido = self.cleaned_data['apellido_paterno']
        if not apellido.replace(" ", "").isalpha():
            raise ValidationError("El apellido paterno solo debe contener letras.")
        return apellido

    def clean_curp(self):
        curp = self.cleaned_data['curp']
        if len(curp) != 18:
            raise ValidationError("La CURP debe tener exactamente 18 caracteres.")
        return curp.upper()

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        if not telefono.isdigit() or len(telefono) != 10:
            raise ValidationError("El teléfono debe contener exactamente 10 números.")
        return telefono

    def clean_contraseña_hash(self):
        contraseña = self.cleaned_data['contraseña_hash']
        if len(contraseña) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r"[A-Za-z]", contraseña):
            raise ValidationError("La contraseña debe contener al menos una letra.")
        if not re.search(r"[0-9]", contraseña):
            raise ValidationError("La contraseña debe contener al menos un número.")
        if not re.search(r"[!@#$%^&*()_+{}\[\]:;<>,.?~\\-]", contraseña):
            raise ValidationError("La contraseña debe contener al menos un carácter especial.")
        return contraseña

    def clean(self):
        cleaned_data = super().clean()
        contraseña = cleaned_data.get("contraseña_hash")
        confirmar = cleaned_data.get("confirmar_contraseña")
        if contraseña and confirmar and contraseña != confirmar:
            self.add_error('confirmar_contraseña', "Las contraseñas no coinciden.")

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.rol_id = self.cleaned_data['rol_id']
        usuario.contraseña_hash = make_password(self.cleaned_data["contraseña_hash"])
        if commit:
            usuario.save()
        return usuario