from django.db import models
from registro.models import Rol, Usuario

class Profesor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    fecha_ingreso = models.DateField()
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Femenino')])
    direccion = models.CharField(max_length=255)
    grupo = models.ForeignKey("gestion.Grupo", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.usuario.nombre} {self.usuario.apellido_paterno}"


class Grupo(models.Model):
    GRADO_CHOICES = [
        ('1', '1°'),
        ('2', '2°'),
        ('3', '3°'),
    ]

    SECCION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    ]

    grado = models.CharField(max_length=1, choices=GRADO_CHOICES)
    seccion = models.CharField(max_length=1, choices=SECCION_CHOICES)
    ciclo_escolar = models.CharField(max_length=20, default="2025-2026")  

    class Meta:
        unique_together = ('grado', 'seccion', 'ciclo_escolar') 
        verbose_name_plural = 'Grupos'

    def __str__(self):
        return f"{self.grado}°{self.seccion}"
    

class Alumno(models.Model):
    nombre_completo = models.CharField(max_length=100)
    curp = models.CharField(max_length=18, unique=True)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=10, choices=[('Masculino', 'Masculino'), ('Femenino', 'Femenino')])

    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)

    # Datos del tutor (por ahora sin ForeignKey)
    tutor_nombre = models.CharField(max_length=100)
    tutor_telefono = models.CharField(max_length=15)
    tutor_curp = models.CharField(max_length=18)

    # Relación opcional con Usuario tutor (nuevo campo)
    tutor_usuario = models.ForeignKey(
        Usuario,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={'rol__nombre': 'Tutor'},
        related_name='alumnos'
    )

    def __str__(self):
        return self.nombre_completo

class MateriaBase(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Materia(models.Model):
    GRADO_CHOICES = [
        ('1', '1°'),
        ('2', '2°'),
        ('3', '3°'),
    ]

    materia_base = models.ForeignKey(MateriaBase, on_delete=models.CASCADE)
    grado = models.CharField(max_length=1, choices=GRADO_CHOICES)

    class Meta:
        unique_together = ('materia_base', 'grado')

    def __str__(self):
        return f"{self.materia_base.nombre} (Grado {self.grado})"


class AsignacionMateria(models.Model):
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE)
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('profesor', 'grupo', 'materia')

    def __str__(self):
        return f"{self.profesor} - {self.materia} - {self.grupo}"

class Calificacion(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    trimestre = models.IntegerField(choices=[(1, '1° Trimestre'), (2, '2° Trimestre'), (3, '3° Trimestre')])
    calificacion = models.DecimalField(max_digits=4, decimal_places=2)

    class Meta:
        unique_together = ('alumno', 'materia', 'trimestre')

    def __str__(self):
        return f"{self.alumno} - {self.materia} - T{self.trimestre}: {self.calificacion}"
