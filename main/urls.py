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
]
