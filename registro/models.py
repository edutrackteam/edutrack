from django.db import models

class Rol(models.Model):
    nombre = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nombre

class Usuario(models.Model):
    curp = models.CharField(max_length=18, unique=True)
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=15)
    contraseña_hash = models.CharField(max_length=128)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    # Este campo solo aplicará a profesores
    grupo = models.ForeignKey('gestion.Grupo', null=True, blank=True, on_delete=models.SET_NULL)

    foto = models.ImageField(upload_to='fotos_usuarios/', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} ({self.rol.nombre})"
