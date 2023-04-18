from django.shortcuts import render
from django.views.generic import TemplateView

from main.models import *


# Create your views here.

class PerfilCliente(TemplateView):
    template_name = 'main/perfil.html'
    model= Perfil
    def get(self, request, *args, **kwargs):
        user = request.user
        num_user = user.id
        perfil = Perfil.objects.filter(usuario_id=num_user)
        "compras = self.model.objects.filter(perfil_id=perfil[0].id)"
        "pago = Metodo_pago.objects.filter(perfil_id=perfil[0].id)"

        return render(request, self.template_name, {'perfil': perfil})
