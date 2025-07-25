from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from gestion.models import Profesor, Grupo, Alumno, Materia, AsignacionMateria, Calificacion, MateriaBase
from registro.models import Usuario, Rol
from gestion.forms import ProfesorForm, GrupoForm, AlumnoForm, MateriaForm
from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.template.loader import get_template
from weasyprint import HTML
from datetime import date
import openpyxl
from django.contrib.auth import logout

# Función para listar todos los profesores de la aplicacion
def lista_profesores(request):
    if 'usuario_id' not in request.session:
        return redirect('login_admin')
    
    if request.method == 'POST':
        # Datos de usuario
        nombre = request.POST['nombre']
        apellido_paterno = ""  # Puedes agregarlo al formulario si quieres
        apellido_materno = ""
        correo = request.POST['correo']
        telefono = request.POST['telefono']
        curp = request.POST['curp']
        rol_profesor = Rol.objects.get(nombre='Profesor')

        # Crear usuario
        usuario = Usuario.objects.create(
            nombre=nombre,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            correo=correo,
            contraseña_hash=make_password("temporal123"),
            curp=curp,
            telefono=telefono,
            rol=rol_profesor
        )

        # Datos de profesor
        fecha_ingreso = request.POST['fecha_ingreso']
        fecha_nacimiento = request.POST['fecha_nacimiento']
        sexo = request.POST['sexo']
        direccion = request.POST['direccion']
        grupo_id = request.POST['grupo']

        # Crear profesor
        Profesor.objects.create(
            usuario=usuario,
            fecha_ingreso=fecha_ingreso,
            fecha_nacimiento=fecha_nacimiento,
            sexo=sexo,
            direccion=direccion,
            grupo_id=grupo_id
        )

        messages.success(request, "Profesor registrado correctamente.")
        return redirect('lista_profesores')

    # Para mostrar lista
    profesores = Profesor.objects.select_related('usuario', 'grupo')
    grupos = Grupo.objects.all()
    return render(request, 'gestion/lista_profesores.html', {'profesores': profesores, 'grupos': grupos})

#Funcion para editar los datos de los profesores por parte de directivos
@csrf_exempt
def editar_profesor(request, profesor_id):
    profesor = get_object_or_404(Profesor, id=profesor_id)

    if request.method == 'POST':
        # Captura los valores del formulario enviado
        usuario = profesor.usuario
        usuario.nombre = request.POST.get('nombre')
        usuario.correo = request.POST.get('correo')
        usuario.curp = request.POST.get('curp')
        usuario.save()

        profesor.fecha_nacimiento = request.POST.get('fecha_nacimiento')
        profesor.sexo = request.POST.get('sexo')
        profesor.telefono = request.POST.get('telefono')
        profesor.direccion = request.POST.get('direccion')
        profesor.fecha_ingreso = request.POST.get('fecha_ingreso')
        grupo_id = request.POST.get('grupo')
        if grupo_id:
            profesor.grupo_id = grupo_id

        messages.success(request, "Datos del profesor acutalizados correctamente")
        profesor.save()
        return JsonResponse({'success': True, 'redirect_url': reverse('lista_profesores')})


    # GET: devolver modal con datos
    return render(request, 'gestion/modals/form_editar_profesor.html', {
        'profesor': profesor,
        'grupos': Grupo.objects.all()
    })

# Función para eliminar a los profesores
@require_POST
def eliminar_profesor(request, profesor_id):
    profesor = get_object_or_404(Profesor, id=profesor_id)
    usuario = profesor.usuario
    profesor.delete()
    usuario.delete()
    messages.success(request, "Profesor eliminado correctamente.")
    return redirect('lista_profesores')

# Función para editar los perfiles de los profesores
def perfil_profesor(request):
    if 'usuario_id' not in request.session:
        return redirect('login_admin')  

    usuario = Usuario.objects.get(id=request.session['usuario_id'])

    if request.method == 'POST' and request.FILES.get('foto'):
        usuario.foto = request.FILES['foto']
        usuario.save()
        return redirect('perfil_profesor')

    return render(request, 'gestion/perfil_profesor.html', {'usuario': usuario})

# Función para ver los datos de los profesores registrados en el sistema
def ver_profesor(request, profesor_id):
    if 'usuario_id' not in request.session:
        return redirect('login_admin')
    
    profesor = get_object_or_404(Profesor, id=profesor_id)
    return render(request, 'gestion/modals/ver_profesor.html', {
        'profesor': profesor
    })

# Función para listar todos los grupos y grados registrados
def lista_grupos(request):
    if 'usuario_id' not in request.session:
        return redirect('login_admin')
    
    grupos = Grupo.objects.all()

    if request.method == 'POST':
        form = GrupoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Grupo registrado correctamente")
            return redirect('lista_grupos')  # o el nombre que tenga tu ruta
    else:
        form = GrupoForm()

    return render(request, 'gestion/lista_grupos.html', {
        'form': form,
        'grupos': grupos
    })

# Función para listar todos los alumnos
def lista_alumnos(request):
    if 'usuario_id' not in request.session:
        return redirect('login_admin')
    
    alumnos = Alumno.objects.select_related('grupo').all()

    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Alumno registrado correctamente.")
            return redirect('lista_alumnos')
    else:
        form = AlumnoForm()

    return render(request, 'gestion/lista_alumnos.html', {
        'alumnos': alumnos,
        'form': form
    })

# Funcion para editar los datos de los alumnos por parte de directivos
@csrf_exempt
def editar_alumno(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    
    if request.method == 'POST':
        alumno.nombre = request.POST.get('nombre')
        alumno.curp = request.POST.get('curp')
        alumno.sexo = request.POST.get('sexo')
        alumno.fecha_nacimiento = request.POST.get('fecha_nacimiento')
        alumno.direccion = request.POST.get('direccion')
        alumno.telefono = request.POST.get('telefono')
        alumno.correo = request.POST.get('correo')
        alumno.nombre_tutor = request.POST.get('nombre_tutor')
        alumno.grupo_id = request.POST.get('grupo')
        messages.success(request, "Datos del alumno acutalizados correctamente")
        alumno.save()

        return JsonResponse({'success': True})

    return render(request, 'gestion/modals/form_editar_alumno.html', {
        'alumno': alumno,
        'grupos': Grupo.objects.all()
    })

# Función  para eliminar alumnos por parte de directivos
@require_POST
def eliminar_alumno(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    alumno.delete()
    messages.success(request, "Alumno eliminado correctamente.")
    return redirect('lista_alumnos')

# Función para listar los alumnos por grado y grupo
def ver_alumnos_grupo(request, grupo_id):
    if 'usuario_id' not in request.session:
        return redirect('login_admin')
    
    grupo = get_object_or_404(Grupo, id=grupo_id)
    alumnos = Alumno.objects.filter(grupo=grupo)
    return render(request, 'gestion/alumnos_por_grupo.html', {
        'grupo': grupo,
        'alumnos': alumnos
    })

# Funcion para ver las materias
def lista_materias(request):
    if 'usuario_id' not in request.session:
        return redirect('login_admin')

    materias = Materia.objects.select_related('materia_base').all().order_by('grado', 'materia_base__nombre')
    materias_base = MateriaBase.objects.all().order_by('nombre')

    if request.method == 'POST':
        materia_base_id = request.POST.get('materia_base')
        nueva_materia_nombre = request.POST.get('nueva_materia')
        grado = request.POST.get('grado')

        if materia_base_id == 'otro':
            # Crear nueva materia base si no existe
            if not nueva_materia_nombre:
                messages.error(request, "Debes ingresar el nombre de la nueva materia.")
                return redirect('lista_materias')
            materia_base, created = MateriaBase.objects.get_or_create(nombre=nueva_materia_nombre)
        else:
            materia_base = MateriaBase.objects.get(id=materia_base_id)

        # Verificar si ya existe la materia para ese grado
        if Materia.objects.filter(materia_base=materia_base, grado=grado).exists():
            messages.error(request, "La materia ya existe para ese grado.")
        else:
            Materia.objects.create(materia_base=materia_base, grado=grado)
            messages.success(request, "Materia agregada correctamente.")

        return redirect('lista_materias')

    context = {
        'materias': materias,
        'materias_base': materias_base,
    }
    return render(request, 'gestion/lista_materias.html', context)

# Función para editar los nombres de las materias
@csrf_exempt
def editar_materia_base(request, materia_base_id):
    materia_base = get_object_or_404(MateriaBase, id=materia_base_id)

    if request.method == 'POST':
        nuevo_nombre = request.POST.get('nombre', '').strip()
        if not nuevo_nombre:
            return JsonResponse({'success': False, 'error': 'El nombre no puede estar vacío.'})

        # Verificar si existe otro con ese nombre
        if MateriaBase.objects.exclude(id=materia_base.id).filter(nombre__iexact=nuevo_nombre).exists():
            return JsonResponse({'success': False, 'error': 'Ya existe otra materia con ese nombre.'})

        materia_base.nombre = nuevo_nombre
        materia_base.save()
        return JsonResponse({'success': True})

    # Si es GET, retornar un modal con formulario (o plantilla)
    return render(request, 'gestion/modals/form_editar_materia_base.html', {'materia_base': materia_base})

    context = {
        'asignaciones': asignaciones,
        'profesores': Profesor.objects.all(),
        'grupos': Grupo.objects.all(),
        'materias': Materia.objects.all(),
    }
    return render(request, 'gestion/asignaciones_materias.html', context)

# Función para la vista panel profesor
def panel_profesor(request):
    if 'usuario_id' not in request.session:
        return redirect('login_admin')

    usuario_id = request.session.get('usuario_id')
    usuario = get_object_or_404(Usuario, id=usuario_id)
    profesor = get_object_or_404(Profesor, usuario=usuario)

    alumnos = Alumno.objects.filter(grupo=profesor.grupo) if profesor.grupo else []

    # Obtener materias del grado del grupo del profesor
    materias = Materia.objects.filter(grado=profesor.grupo.grado) if profesor.grupo else []

    return render(request, 'gestion/panel_profesor.html', {
        'profesor': profesor,
        'alumnos': alumnos,
        'materias': materias,
        'usuario':usuario
    })

# Función para guardar calificaciones del profesor
def registrar_calificacion_alumno(request, alumno_id, materia_id):
    if 'usuario_id' not in request.session:
        return redirect('login_admin')

    alumno = get_object_or_404(Alumno, id=alumno_id)
    materia = get_object_or_404(Materia, id=materia_id)
    
    usuario = Usuario.objects.get(id=request.session['usuario_id'])

    if request.method == 'POST':
        trimestre = int(request.POST.get('trimestre'))
        valor = request.POST.get('calificacion')

        calificacion, created = Calificacion.objects.update_or_create(
            alumno=alumno,
            materia=materia,
            trimestre=trimestre,
            defaults={'calificacion': valor}
        )
        messages.success(request, f"Calificación guardada para {alumno.nombre_completo}")
        return redirect('registrar_calificacion_alumno', alumno_id=alumno.id, materia_id=materia.id)

    return render(request, 'gestion/registrar_calificacion_alumno.html', {
        'alumno': alumno,
        'materia': materia,
        'usuario':usuario,
    })

# Función para ver calificaciones para profesores
def ver_calificaciones(request):
    if 'usuario_id' not in request.session:
        return redirect('login_admin')

    usuario_id = request.session.get('usuario_id')
    profesor = get_object_or_404(Profesor, usuario_id=usuario_id)
    usuario = profesor.usuario

    grupo = profesor.grupo
    alumnos = Alumno.objects.filter(grupo=grupo) if grupo else []

    return render(request, 'gestion/ver_calificaciones.html', {
        'grupo': grupo,
        'alumnos': alumnos,
        'usuario': usuario, 
    })

# Funcion boleta para profesores
def ver_boleta(request, alumno_id):
    if 'usuario_id' not in request.session:
        return redirect('login_admin')

    alumno = get_object_or_404(Alumno, id=alumno_id)
    calificaciones = Calificacion.objects.filter(alumno=alumno).select_related('materia')
    grupo = alumno.grupo
    profesor = Profesor.objects.filter(grupo=grupo).first()
    usuario = profesor.usuario 
    
    datos = {}
    for cal in calificaciones:
        materia_nombre = cal.materia.materia_base.nombre  # aquí cambio
        if materia_nombre not in datos:
            datos[materia_nombre] = {'1': '', '2': '', '3': '', 'promedio': ''}
        datos[materia_nombre][str(cal.trimestre)] = cal.calificacion
    
    for materia, trimestres in datos.items():
        try:
            notas = []
            for t in range(1, 4):
                valor = trimestres.get(str(t), '')
                if valor == '':
                    valor = 0  # Si no hay calificación, se toma como 0
                notas.append(float(valor))
            trimestres['promedio'] = round(sum(notas) / 3, 2)
        except:
            trimestres['promedio'] = ''
    
    return render(request, 'gestion/ver_boleta.html', {
        'alumno': alumno,
        'profesor' : profesor,
        'boleta': datos,
        'usuario': usuario
    })

# Función boleta directivos
def ver_boleta_directivo(request, alumno_id):
    if 'usuario_id' not in request.session:
        return redirect('login_admin')

    alumno = get_object_or_404(Alumno, id=alumno_id)
    calificaciones = Calificacion.objects.filter(alumno=alumno).select_related('materia')
    grupo = alumno.grupo
    profesor = Profesor.objects.filter(grupo=grupo).first()
    
    datos = {}
    for cal in calificaciones:
        materia_nombre = cal.materia.materia_base.nombre  # aquí cambio
        if materia_nombre not in datos:
            datos[materia_nombre] = {'1': '', '2': '', '3': '', 'promedio': ''}
        datos[materia_nombre][str(cal.trimestre)] = cal.calificacion
    
    for materia, trimestres in datos.items():
        try:
            notas = []
            for t in range(1, 4):
                valor = trimestres.get(str(t), '')
                if valor == '':
                    valor = 0  # Si no hay calificación, se toma como 0
                notas.append(float(valor))
            trimestres['promedio'] = round(sum(notas) / 3, 2)
        except:
            trimestres['promedio'] = ''
    
    return render(request, 'gestion/ver_boleta_directivo.html', {
        'alumno': alumno,
        'profesor' : profesor,
        'boleta': datos,
    })

# Función para gener la boleta en PDF
def boleta_pdf(request, alumno_id):
    if 'usuario_id' not in request.session:
        return redirect('login_admin')

    alumno = get_object_or_404(Alumno, id=alumno_id)
    grupo = alumno.grupo
    profesor = Profesor.objects.filter(grupo=grupo).first()

    boleta = {}
    materias = Materia.objects.filter(grado=alumno.grupo.grado)

    for materia in materias:
        califs = Calificacion.objects.filter(alumno=alumno, materia=materia)
        trimestre_dict = {1: None, 2: None, 3: None}  # None = Sin calificación registrada

        for cal in califs:
            if cal.trimestre in [1, 2, 3]:
                try:
                    trimestre_dict[cal.trimestre] = float(cal.calificacion)
                except:
                    trimestre_dict[cal.trimestre] = None

        # Calcular promedio dividiendo entre 3 y tomando como 0 si falta
        notas = []
        for t in [1, 2, 3]:
            valor = trimestre_dict[t]
            if valor is None:
                valor = 0
            notas.append(valor)

        promedio = round(sum(notas) / 3, 2)

        boleta[materia.materia_base.nombre] = {
            "1": str(trimestre_dict[1]) if trimestre_dict[1] is not None else "-",
            "2": str(trimestre_dict[2]) if trimestre_dict[2] is not None else "-",
            "3": str(trimestre_dict[3]) if trimestre_dict[3] is not None else "-",
            "promedio": str(promedio),
        }

    template = get_template("gestion/boleta_pdf.html")
    html_content = template.render({
        "alumno": alumno,
        "profesor": profesor,
        "boleta": boleta,
        "fecha": date.today().strftime("%d/%m/%Y"),
    })

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'inline; filename="boleta_{alumno.nombre_completo}.pdf"'

    HTML(string=html_content).write_pdf(response)

    return response

# Función para el panel tutor
def panel_tutor(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    usuario_id = request.session.get('usuario_id')
    tutor = Usuario.objects.filter(id=usuario_id, rol__nombre="Tutor").first()
    alumno = None
    mensaje = None

    if request.method == 'POST':
        curp_alumno = request.POST.get('curp_alumno', '').strip().upper()

        # Buscar alumno por CURP
        try:
            alumno = Alumno.objects.get(curp=curp_alumno)
            if alumno.tutor_usuario == tutor:
                mensaje = "Este alumno ya está vinculado a ti."
            else:
                alumno.tutor_usuario = tutor
                alumno.save()
                mensaje = f"Alumno {alumno.nombre_completo} vinculado exitosamente."
        except Alumno.DoesNotExist:
            mensaje = "No se encontró ningún alumno con esa CURP."

    # Mostrar los alumnos vinculados para ese tutor
    alumnos_vinculados = Alumno.objects.filter(tutor_usuario=tutor)

    return render(request, 'gestion/panel_tutor.html', {
        'tutor': tutor,
        'mensaje': mensaje,
        'alumnos': alumnos_vinculados,
    })

# Función ver boleta para los padres de familia (tutor)
def ver_boleta_tutor(request, alumno_id):
    if 'usuario_id' not in request.session:
        return redirect('login_admin')

    alumno = get_object_or_404(Alumno, id=alumno_id)
    calificaciones = Calificacion.objects.filter(alumno=alumno).select_related('materia')
    grupo = alumno.grupo
    profesor = Profesor.objects.filter(grupo=grupo).first()
    
    datos = {}
    for cal in calificaciones:
        materia_nombre = cal.materia.materia_base.nombre  # aquí cambio
        if materia_nombre not in datos:
            datos[materia_nombre] = {'1': '', '2': '', '3': '', 'promedio': ''}
        datos[materia_nombre][str(cal.trimestre)] = cal.calificacion
    
    for materia, trimestres in datos.items():
        try:
            notas = []
            for t in range(1, 4):
                valor = trimestres.get(str(t), '')
                if valor == '':
                    valor = 0  # Si no hay calificación, se toma como 0
                notas.append(float(valor))
            trimestres['promedio'] = round(sum(notas) / 3, 2)
        except:
            trimestres['promedio'] = ''
    
    return render(request, 'gestion/ver_boleta_tutor.html', {
        'alumno': alumno,
        'profesor' : profesor,
        'boleta': datos,
    })

def importar_alumnos_excel(request):
    if request.method == 'POST' and request.FILES.get('archivo_excel'):
        archivo = request.FILES['archivo_excel']

        try:
            wb = openpyxl.load_workbook(archivo)
            hoja = wb.active

            for fila in hoja.iter_rows(min_row=2, values_only=True):
                nombre_completo, curp, fecha_nacimiento, sexo, tutor_nombre, tutor_telefono, tutor_curp, grupo_nombre = fila

                if not grupo_nombre or len(str(grupo_nombre)) < 2:
                    messages.warning(request, f"Formato de grupo inválido: {grupo_nombre}")
                    continue

                grado = str(grupo_nombre)[:-1]  # "1A" → "1"
                seccion = str(grupo_nombre)[-1]  # "1A" → "A"

                grupo = Grupo.objects.filter(grado=grado, seccion=seccion).first()

                if not grupo:
                    messages.warning(request, f"El grupo '{grupo_nombre}' no existe. Alumno {nombre_completo} omitido.")
                    continue

                if Alumno.objects.filter(curp=curp).exists():
                    messages.warning(request, f"El alumno con CURP {curp} ya existe. No se registró duplicado.")
                    continue

                Alumno.objects.create(
                    nombre_completo=nombre_completo,
                    curp=curp,
                    fecha_nacimiento=fecha_nacimiento,
                    sexo=sexo,
                    tutor_nombre=tutor_nombre,
                    tutor_telefono=str(tutor_telefono),
                    tutor_curp=tutor_curp,
                    grupo=grupo
                )

            messages.success(request, "Alumnos importados correctamente.")
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {e}")
    else:
        messages.error(request, "Debes subir un archivo Excel.")

    return redirect('lista_alumnos')

# Funcion para cerrar sesión
def logout_view(request):
    rol = request.session.get('rol') 
    logout(request)

    # De acuerdo al rol del usuario, lo redirige a su login correspondiente
    if rol == 'Tutor':
        return redirect('login')
    elif rol == 'Profesor':
        return redirect('login_admin')
    elif rol == 'Directivo':
        return redirect('login_admin')
    else:
        return redirect('home')  
