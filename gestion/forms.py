from datetime import date
from django import forms
from registro.models import Usuario, Rol
from gestion.models import Grupo
from django import forms
from .models import Alumno, Materia, MateriaBase
from django.core.exceptions import ValidationError
from datetime import date
import re

class ProfesorForm(forms.ModelForm):
    grupo = forms.ModelChoiceField(queryset=Grupo.objects.all(), label="Grupo")
    
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido_paterno', 'apellido_materno', 'correo', 'contraseña_hash', 'grupo']
        widgets = {
            'contraseña_hash': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fijar rol automáticamente a "Profesor"
        self.fields['grupo'].empty_label = "Selecciona un grupo"

class GrupoForm(forms.ModelForm):
    class Meta:
        model = Grupo
        fields = ['grado', 'seccion']
        labels = {
            'grado': 'Grado',
            'seccion': 'Sección'
        }

    def clean(self):
        cleaned_data = super().clean()
        grado = cleaned_data.get('grado')
        seccion = cleaned_data.get('seccion')
        ciclo_escolar = "2025-2026"  # o dinámico si se selecciona en el frontend

        if Grupo.objects.filter(grado=grado, seccion=seccion, ciclo_escolar=ciclo_escolar).exists():
            raise forms.ValidationError(f"El grupo {grado}°{seccion} ya existe para el ciclo escolar {ciclo_escolar}.")

class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumno
        fields = '__all__'
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_nombre_completo(self):
        nombre = self.cleaned_data.get('nombre_completo')
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$', nombre):
            raise ValidationError('El nombre solo debe contener letras y espacios.')
        return nombre

    def clean_curp(self):
        curp = self.cleaned_data.get('curp')
        if len(curp or '') != 18:
            raise ValidationError('La CURP debe tener exactamente 18 caracteres.')
        return curp.upper()

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')
        if fecha:
            edad = (date.today() - fecha).days // 365
            if edad < 10:
                raise ValidationError('El alumno debe tener al menos 10 años.')
        return fecha

    def clean_tutor_nombre(self):
        tutor_nombre = self.cleaned_data.get('tutor_nombre')
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$', tutor_nombre):
            raise ValidationError('El nombre del tutor solo debe contener letras y espacios.')
        return tutor_nombre

    def clean_tutor_telefono(self):
        telefono = self.cleaned_data.get('tutor_telefono')
        if not telefono.isdigit() or len(telefono) != 10:
            raise ValidationError('El teléfono debe contener exactamente 10 números.')
        return telefono

    def clean_tutor_curp(self):
        tutor_curp = self.cleaned_data.get('tutor_curp')
        if len(tutor_curp or '') != 18:
            raise ValidationError('La CURP del tutor debe tener exactamente 18 caracteres.')
        return tutor_curp.upper()


class MateriaForm(forms.ModelForm):
    materia_base = forms.ModelChoiceField(
        queryset=MateriaBase.objects.all(),
        empty_label="Selecciona una materia",
        required=False
    )
    nueva_materia = forms.CharField(max_length=100, required=False, label="Otra materia")

    class Meta:
        model = Materia
        fields = ['materia_base', 'nueva_materia', 'grado']

    def clean(self):
        cleaned_data = super().clean()
        materia_base = cleaned_data.get('materia_base')
        nueva_materia = cleaned_data.get('nueva_materia')

        if not materia_base and not nueva_materia:
            raise forms.ValidationError("Debes seleccionar una materia o ingresar una nueva.")

        if materia_base and nueva_materia:
            raise forms.ValidationError("Selecciona solo una opción: materia existente o nueva.")

        return cleaned_data

    def save(self, commit=True):
        materia_base = self.cleaned_data.get('materia_base')
        nueva_materia = self.cleaned_data.get('nueva_materia')

        if nueva_materia:
            materia_base, created = MateriaBase.objects.get_or_create(nombre=nueva_materia)

        self.instance.materia_base = materia_base
        return super().save(commit)