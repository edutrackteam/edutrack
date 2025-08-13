from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_tutor, name='registro_tutor'),
    path('login-admin/', views.login_admin_docente, name='login_admin'),
    path('registro-admin/', views.registro_admin, name='registro_admin'),
]
