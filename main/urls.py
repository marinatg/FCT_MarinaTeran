from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import static
from django.conf import settings
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    #ruta para establecer idioma
    path('i18n/', include('django.conf.urls.i18n')),
    #path('', TemplateView.as_view(template_name='main/index.html'), name='welcome'),
    path('', views.ListadoEventos.as_view(), name='listadoEventos'),
    path('main/perfil/', views.PerfilCliente.as_view(), name='perfil'),
    path('main/registro/', views.Registro.as_view(), name='registro'),
    path('main/cerrarSesion/', views.CerrarSesion.as_view(), name='cerrarSesion'),
    path('main/iniciarSesion/', views.IniciarSesion.as_view(), name='iniciarSesion'),
    path('main/agregarPerfil/', views.AgregarPerfil.as_view(template_name='main/agregarPerfil.html'), name='agregarPerfil'),
    path('main/editarPerfil/<int:pk>', views.EditarPerfil.as_view(template_name='main/editarPerfil.html'), name='editarPerfil'),
    path('main/eliminarPerfil/<int:pk>', views.EliminarPerfil.as_view(template_name='main/eliminar.html'), name='eliminarPerfil'),
    path('main/eventoDetalle/<int:pk>', views.EventoDetalle.as_view(), name='eventoDetalle'),
    path('PanelAdmin/panelAdmin/', views.PanelAdmin.as_view(), name='panelAdmin'),
    path('PanelAdmin/administrarSala/<int:pk>', views.AdministrarSala.as_view(), name='administrarSala'),
    path('PanelAdmin/administrarEvento/<int:pk>', views.AdministrarEvento.as_view(), name='administrarEvento'),
    path('PanelAdmin/agregarSala/', views.AgregarSala.as_view(template_name='PanelAdmin/agregarSala.html'), name='agregarSala'),
    path('PanelAdmin/editarSala/<int:pk>', views.EditarSala.as_view(template_name='PanelAdmin/editarSala.html'), name='editarSala'),
    path('PanelAdmin/eliminarSala/<int:pk>', views.EliminarSala.as_view(template_name='PanelAdmin/eliminar.html'), name='eliminarSala'),
    path('PanelAdmin/agregarEvento/', views.AgregarEvento.as_view(template_name='PanelAdmin/agregarEvento.html'), name='agregarEvento'),
    path('PanelAdmin/editarEvento/<int:pk>', views.EditarEvento.as_view(template_name='PanelAdmin/editarEvento.html'), name='editarEvento'),
    path('PanelAdmin/eliminarEvento/<int:pk>', views.EliminarEvento.as_view(template_name='PanelAdmin/eliminar.html'), name='eliminarEvento'),
    path('PanelAdmin/asignarPrecioZonaEvento/', views.AsignarPrecioZonaEvento.as_view(template_name='PanelAdmin/asignarPrecioZonaEvento.html'), name='asignarPrecioZonaEvento'),
    path('main/paypal/', views.Paypal.as_view(template_name='main/paypal.html'), name='paypal'),
    path('main/pago/', views.pago, name= 'pago'),
    # path('main/generar_pdf/', views.generar_pdf, name='generar_pdf'),
    path('main/resumenCompra/', views.ResumenCompra.as_view(template_name='main/resumenCompra.html'), name='resumenCompra'),
    path('main/compraDetalle/<int:pk>', views.CompraDetalle.as_view(template_name='main/resumenCompra.html'), name='compraDetalle'),



  ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
