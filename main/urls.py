from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    #ruta para establecer idioma
    path('i18n/', include('django.conf.urls.i18n')),
    path('', TemplateView.as_view(template_name='main/index.html'), name='welcome'),
    path('main/perfil/', views.PerfilCliente.as_view(), name='perfil'),
    path('main/registro/', views.Registro.as_view(), name='registro'),
    path('main/cerrarSesion/', views.CerrarSesion.as_view(), name='cerrarSesion'),
    path('main/iniciarSesion/', views.IniciarSesion.as_view(), name='iniciarSesion'),
    path('main/agregarPerfil/', views.AgregarPerfil.as_view(template_name='main/agregarPerfil.html'),
         name='agregarPerfil'),
    path('main/editarPerfil/<int:pk>',
         views.EditarPerfil.as_view(template_name='main/editarPerfil.html'), name='editarPerfil'),
    path('main/eliminarPerfil/<int:pk>',
         views.EliminarPerfil.as_view(template_name='main/eliminar.html'), name='eliminarPerfil'),
    path('administrador/agregarMetodoPago/',
         views.AgregarMetodoPago.as_view(template_name='main/agregarMetodoPago.html'),
         name='agregarMetodoPago'),
    path('administrador/editarMetodoPago/<int:pk>',
         views.EditarMetodoPago.as_view(template_name='main/editarMetodoPago.html'), name='editarMetodoPago'),
    path('administrador/eliminarMetodoPago/<int:pk>',
         views.EliminarMetodoPago.as_view(template_name='main/eliminar.html'), name='eliminarMetodoPago'),
]
