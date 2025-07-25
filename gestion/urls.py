from django.urls import path
from . import views

urlpatterns = [
    # === Profesores ===
    path('profesores/', views.lista_profesores, name='lista_profesores'),
    path('profesores/editar/<int:profesor_id>/', views.editar_profesor, name='editar_profesor'),
    path('profesores/eliminar/<int:profesor_id>/', views.eliminar_profesor, name='eliminar_profesor'),
    path('profesores/ver/<int:profesor_id>/', views.ver_profesor, name='ver_profesor'),
    path('perfil/', views.perfil_profesor, name='perfil_profesor'),

    # === Grupos ===
    path('grupos/', views.lista_grupos, name='lista_grupos'),
    path('grupo/<int:grupo_id>/alumnos/', views.ver_alumnos_grupo, name='ver_alumnos_grupo'),

    # === Alumnos ===
    path('alumnos/', views.lista_alumnos, name='lista_alumnos'),
    path('alumnos/editar/<int:alumno_id>/', views.editar_alumno, name='editar_alumno'),
    path('alumnos/eliminar/<int:alumno_id>/', views.eliminar_alumno, name='eliminar_alumno'),
    path('alumnos/importar_excel/', views.importar_alumnos_excel, name='importar_alumnos_excel'),

    # === Materias ===
    path('materias/', views.lista_materias, name='lista_materias'),
    path('materias/editar/<int:materia_base_id>/', views.editar_materia_base, name='editar_materia_base'),

    # === Calificaciones ===
    path('registrar_calificacion/alumno/<int:alumno_id>/<int:materia_id>/', views.registrar_calificacion_alumno, name='registrar_calificacion_alumno'),
    path('ver_calificaciones/', views.ver_calificaciones, name='ver_calificaciones'),

    # === Boletas ===
    path('boleta/<int:alumno_id>/', views.ver_boleta, name='ver_boleta'),
    path('boleta/directivo/<int:alumno_id>/', views.ver_boleta_directivo, name='ver_boleta_directivo'),
    path('boleta/tutor/<int:alumno_id>/', views.ver_boleta_tutor, name='ver_boleta_tutor'),
    path('boleta-pdf/<int:alumno_id>/', views.boleta_pdf, name='boleta_pdf'),

    # === Paneles ===
    path('panel_profesor/', views.panel_profesor, name='panel_profesor'),
    path('panel_tutor/', views.panel_tutor, name='panel_tutor'),

    # === Autenticación ===
    path('logout/', views.logout_view, name='logout'),
]
