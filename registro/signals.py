from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Rol

@receiver(post_migrate)
def crear_roles_por_defecto(sender, **kwargs):
    if sender.name == 'registro':  # Solo al migrar esta app
        roles = ["Profesor", "Tutor", "Directivo"]
        for nombre in roles:
            Rol.objects.get_or_create(nombre=nombre)
