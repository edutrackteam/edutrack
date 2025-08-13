from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from .forms import RegistroTutorForm, LoginForm, LoginAdminForm, RegistroAdminForm
from .models import Usuario, Rol
import requests

def registro_tutor(request):
    if request.method == 'POST':
        form = RegistroTutorForm(request.POST)
        if form.is_valid():
            curp = form.cleaned_data['curp']
            if Usuario.objects.filter(curp=curp).exists():
                form.add_error('curp', "Este CURP ya está registrado.")
            else:
                # Crear o recuperar el rol "Tutor"
                rol_tutor, _ = Rol.objects.get_or_create(nombre="Tutor")
                usuario = form.save(commit=False)
                usuario.rol = rol_tutor
                usuario.save()
                messages.success(request, "¡Registro exitoso! Ahora puedes iniciar sesión.")
                return redirect('login')
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = RegistroTutorForm()
    return render(request, 'registro_tutor.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        # Obtener respuesta del recaptcha del POST
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': '6LeYgI4rAAAAANPqWshpB4dlmaaHf0UC5ngop4Os',
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if not result.get('success'):
            messages.error(request, 'reCAPTCHA no válido. Intenta nuevamente.')
            return render(request, 'login.html', {'form': form})

        if form.is_valid():
            correo = form.cleaned_data['correo']
            contraseña = form.cleaned_data['contraseña']

            try:
                usuario = Usuario.objects.get(correo=correo)

                if usuario.rol.nombre.lower() != 'tutor':
                    messages.error(request, "Este usuario no tiene permisos de Tutor.")
                elif check_password(contraseña, usuario.contraseña_hash):
                    request.session['usuario_id'] = usuario.id
                    request.session['nombre_usuario'] = f"{usuario.nombre} {usuario.apellido_paterno}"
                    request.session['rol'] = usuario.rol.nombre

                    messages.success(request, f"Bienvenido, {usuario.nombre}")
                    return redirect('panel_tutor')
                else:
                    messages.error(request, "Contraseña incorrecta")
            except Usuario.DoesNotExist:
                messages.error(request, "Correo no registrado")
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})


def login_admin_docente(request):
    if request.method == 'POST':
        form = LoginAdminForm(request.POST)

        # Validar reCAPTCHA
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': '6LeYgI4rAAAAANPqWshpB4dlmaaHf0UC5ngop4Os',
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if not result.get('success'):
            messages.error(request, 'reCAPTCHA no válido. Intenta nuevamente.')
            roles = Rol.objects.filter(nombre__in=["Profesor", "Directivo"])
            return render(request, 'login_admin_docente.html', {
                'form': form,
                'roles': roles
            })

        if form.is_valid():
            correo = form.cleaned_data['correo']
            contraseña = form.cleaned_data['contraseña']
            rol_id = int(form.cleaned_data['rol'])

            try:
                usuario = Usuario.objects.get(correo=correo, rol_id=rol_id)

                if usuario.rol.nombre not in ['Profesor', 'Directivo']:
                    messages.error(request, "Este usuario no tiene permisos de Directivo/Profesor.")
                elif check_password(contraseña, usuario.contraseña_hash):
                    request.session['usuario_id'] = usuario.id
                    request.session['nombre_usuario'] = f"{usuario.nombre} {usuario.apellido_paterno}"
                    request.session['rol_id'] = usuario.rol.id
                    request.session['rol'] = usuario.rol.nombre

                    messages.success(request, f"Bienvenido, {usuario.nombre}")

                    # Redirección según rol
                    if usuario.rol.nombre == 'Directivo':
                        return redirect('lista_profesores')
                    elif usuario.rol.nombre == 'Profesor':
                        return redirect('ver_calificaciones')
                else:
                    messages.error(request, "Contraseña incorrecta.")
            except Usuario.DoesNotExist:
                messages.error(request, "Correo no registrado para ese rol.")
    else:
        form = LoginAdminForm()
    
    roles = Rol.objects.filter(nombre__in=["Profesor", "Directivo"])

    return render(request, 'login_admin_docente.html', {
        'form': form,
        'roles': roles
    })


def registro_admin(request):
    if request.method == 'POST':
        form = RegistroAdminForm(request.POST)
        if form.is_valid():
            curp = form.cleaned_data['curp']
            correo = form.cleaned_data['correo']

            if Usuario.objects.filter(curp=curp).exists():
                form.add_error('curp', "Este CURP ya está registrado.")
            elif Usuario.objects.filter(correo=correo).exists():
                form.add_error('correo', "Este correo ya está registrado.")
            else:
                usuario = form.save(commit=False)
                usuario.rol_id = form.cleaned_data['rol_id'].id  # Asigna el rol explícitamente
                usuario.save()
                messages.success(request, "¡Registro exitoso!")
                return redirect('login_admin')
        else:
            messages.error(request, "Corrige los errores en el formulario.")
    else:
        form = RegistroAdminForm()
    
    return render(request, 'registro_admin.html', {'form': form})
