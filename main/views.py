from datetime import date

from cffi.backend_ctypes import unicode
from django.apps import AppConfig
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import *
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView


from main.forms import UnidadesForm, EventoForm
from main.models import *


from paypalcheckoutsdk.orders import OrdersGetRequest, OrdersCaptureRequest
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
import sys, json


# Create your views here.


"""REGISTRO, LOGIN Y LOGOUT"""
class Registro(CreateView):
    template_name = 'main/registro.html'
    form_class = UserCreationForm
    def get_success_url(self):
        return reverse('welcome')

    @transaction.atomic
    def post(self, request, *args, **kwargs):

            if request.POST['password1'] == request.POST['password2']:
                try:
                    user = User.objects.create_user(username=request.POST['username'],
                                                    password=request.POST['password1'])
                    user.save()

                    perfil = Perfil.objects.create(usuario_id=user.id,
                                    dni=request.POST['dni'],
                                    telefono=request.POST['telefono'])

                    perfil.save()

                    login(request, user)
                    return redirect('welcome')
                except:
                    return render(request, "main/registro.html",
                                  {'form': UserCreationForm, 'error': 'El usuario ya existe'})
            return render(request, "main/registro.html",
                          {'form': UserCreationForm, 'error': 'Las contraseñas no coinciden'})

class CerrarSesion(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('listadoEventos')

class IniciarSesion(View):
    def get(self, request, *args, **kwargs):
        form = AuthenticationForm()
        return render(request, 'main/iniciarSesion.html', {'form': AuthenticationForm})

    def post(self, request, *args, **kwargs):
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'main/iniciarSesion.html', {'form': AuthenticationForm, 'error': 'El usuario o la contraseña son incorrectos'})
        else:
            login(request, user)
            return redirect('listadoEventos')


"""PERFIL DE USUARIO"""
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

class AgregarPerfil(CreateView):
    model = Perfil
    template_name = 'main/agregarPerfil.html'
    fields = '__all__'

    def post(self, request, *args, **kwargs):
        nombre = request.POST.get("nombre")
        dni = request.POST.get("dni")
        fecha_nac = request.POST.get("fecha_nac")
        direccion = request.POST.get("direccion")
        user = request.user

        perfil = Perfil.objects.create(nombre=nombre,
                                         dni=dni,
                                         fecha_nac=fecha_nac,
                                         direccion=direccion,
                                         usuario=user)

        perfil.save()
        return redirect('perfil')
    def get_success_url(self):
        return reverse('perfil')

class EditarPerfil(UpdateView):
    model = Perfil
    fields = ['nombre', 'dni', 'fecha_nac', 'direccion']

    def get_success_url(self, **kwargs):
        return reverse('perfil')

class EliminarPerfil(DeleteView):
    model = Perfil
    fields = '__all__'
    def get_success_url(self, *args, **kwargs):
        return reverse('perfil')


"""LISTADO DE EVENTOS Y FILTRADO"""
class ListadoEventos(TemplateView):
    template_name = 'main/index.html'
    def get(self, request, *args, **kwargs):
        evento = Evento.objects.all()

        busqueda = request.GET.get("buscar")
        disponible = request.GET.get("disponibilidad")
        fechaInicio = request.GET.get("fecha")
        fechaFin = request.GET.get("fecha2")

        if busqueda:

            evento = Evento.objects.filter(nombre__icontains=busqueda)

        if disponible:
            if disponible == '2':
                if fechaInicio:
                    if fechaFin:
                        evento = Evento.objects.filter(fecha_hora__gte = fechaInicio, fecha_hora__lte = fechaFin)
                    else:
                        evento = Evento.objects.filter(fecha_hora__gte = fechaInicio)
                else:
                    if fechaFin:
                        evento = Evento.objects.filter(fecha_hora__lte = fechaFin)
                    else:
                        evento = Evento.objects.all()
            else:
                if fechaInicio:
                    if fechaFin:
                        if disponible == '0':
                            evento = Evento.objects.filter(fecha_hora__gte = fechaInicio, fecha_hora__lte = fechaFin, disponibles = '0')
                        else:
                            evento = Evento.objects.filter(fecha_hora__gte=fechaInicio, fecha_hora__lte=fechaFin,
                                                           disponibles__gt = 0)
                    else:
                        if disponible == '0':
                            evento = Evento.objects.filter(fecha_hora__gte = fechaInicio, disponibles = '0')
                        else:
                            evento = Evento.objects.filter(fecha_hora__gte=fechaInicio, disponibles__gt='0')
                else:
                    if fechaFin:
                        if disponible == '0':
                            evento = Evento.objects.filter(fecha_hora__lte = fechaFin, disponibles = '0')
                        else:
                            evento = Evento.objects.filter(fecha_hora__lte = fechaFin, disponibles__gt = '0')
                    else:
                        if disponible == '0':
                            evento = Evento.objects.filter( disponibles = '0')
                        else:
                            evento = Evento.objects.filter(disponibles__gt='0')

        return render(request, self.template_name, {'evento':evento, 'busqueda': busqueda, 'disponible': disponible, 'fechaInicio': fechaInicio, 'fechaFin': fechaFin})

"""EVENTO DETALLE"""

class EventoDetalle(View):
    model = Evento
    form_class = UnidadesForm
    template_name = 'main/eventoDetalle.html'

    def get(self, request, pk, *args, **kwargs):
        zona = request.GET.get("zona")
        evento = Evento.objects.get(id=pk)
        user = request.user
        num_user = user.id
        perfil = Perfil.objects.filter(
            Q(usuario_id=num_user)
        ).distinct()

        zonas = Zona_evento.objects.filter(evento=pk)
        zonita = zona

        if zonita:
            if zonita == '1':
                zonita = 1
                asientos = Asiento_evento.objects.filter(zona_evento=zonas[0].id)
            if zonita == '2':
                zonita = 2
                asientos = Asiento_evento.objects.filter(zona_evento=zonas[1].id)
            if zonita == '3':
                zonita = 3
                asientos = Asiento_evento.objects.filter(zona_evento=zonas[2].id)

        else:
            zonita = 1
            asientos = Asiento_evento.objects.filter(zona_evento=zonas[0].id)

        zonaElegida = Zona_evento.objects.get(evento=pk, zona=zonita)
        unidades = request.GET.get("unidades", "0")
        asientosElegidos = []

        if unidades > "0":

            for i in asientos:
                asientoEvento = request.GET.get(str(i.id), "False")

                if asientoEvento != "False":
                    asientosElegidos.append(asientoEvento)

            """variables sesion"""
            return redirect('paypal')

        return render(request, self.template_name, {'evento': evento, 'perfil': perfil, 'zonas': zonas, 'zonita': zonita, 'asientos': asientos, 'zonaElegida': zonaElegida})

    # @transaction.atomic
    # def post(self, request, pk, *args, **kwargs):
    #     formulario = self.form_class(request.POST)
    #     if formulario.is_valid():
    #     #     contexto = {}
    #     #     contexto['evento'] = Evento.objects.get(id=pk)
    #     #     user = request.user
    #     #     num_user = user.id
    #     #     contexto['perfil'] = Perfil.objects.filter(
    #     #         Q(usuario_id=num_user)
    #     #     ).distinct()
    #         #asientoElegido = formulario.cleaned_data['21', False]
    #         asientoElegido = request.POST.get("21", False)
    #         #unidades = request.POST.get("unidades")
    #         unidades = formulario.cleaned_data['unidades']
    #         print(asientoElegido)
    #         print(unidades)
    #         print(formulario)
    #
    #     return render(request, self.template_name)


"""Panel de administración"""
class PanelAdmin(TemplateView):
    template_name = 'PanelAdmin/panelAdmin.html'

    def get(self, request, *args, **kwargs):
        sala = Sala.objects.all()
        evento = Evento.objects.all()

        return render(request, 'PanelAdmin/panelAdmin.html', {'sala': sala, 'evento': evento})

class AdministrarSala(View):
    model = Sala
    template_name = 'PanelAdmin/administrarSala.html'

    def get(self, request, pk, *args, **kwargs):
        zona = Zona.objects.filter(sala=pk)
        asiento = []
        for i in zona:
            asiento_zona = Asiento.objects.filter(zona=i.id)
            asiento.append(asiento_zona)
        print(len(asiento))
        return render(request, self.template_name, {'zona': zona, 'asiento': asiento})

class AgregarSala(CreateView):
    model = Sala
    template_name = 'PanelAdmin/agregarrSala.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse('panelAdmin')

class EditarSala(UpdateView):
    model = Sala
    fields = '__all__'

    def get_success_url(self, **kwargs):
        return reverse('panelAdmin')

class EliminarSala(DeleteView):
    model = Sala
    fields = '__all__'

    def get_success_url(self, **kwargs):
        return reverse('panelAdmin')
class AgregarEvento(CreateView):
    model = Evento
    template_name = 'PanelAdmin/agregarEvento.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse('panelAdmin')

class EditarEvento(UpdateView):
    model = Evento
    fields = '__all__'

    def get_success_url(self, **kwargs):
        return reverse('panelAdmin')

class EliminarEvento(DeleteView):
    model = Evento
    fields = '__all__'

    def get_success_url(self, **kwargs):
        return reverse('panelAdmin')
class AgregarZona(CreateView):
    model = Zona
    template_name = 'PanelAdmin/agregarZona.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse('panelAdmin')

class EditarZona(UpdateView):
    model = Zona
    fields = '__all__'

    def get_success_url(self, **kwargs):
        return reverse('panelAdmin')

class EliminarZona(DeleteView):
    model = Zona
    fields = '__all__'

    def get_success_url(self, **kwargs):
        return reverse('panelAdmin')

class AgregarAsiento(CreateView):
    model = Asiento
    template_name = 'PanelAdmin/agregarAsiento.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse('panelAdmin')

class EditarAsiento(UpdateView):
    model = Asiento
    fields = '__all__'

    def get_success_url(self, **kwargs):
        return reverse('panelAdmin')

class EliminarAsiento(DeleteView):
    model = Asiento
    fields = '__all__'

    def get_success_url(self, **kwargs):
        return reverse('panelAdmin')

class AdministrarEvento(View):
    model = Evento
    template_name = 'PanelAdmin/administrarEvento.html'

    def get(self, request, pk, *args, **kwargs):
        zona_evento = Zona_evento.objects.filter(evento=pk)
        asiento_evento = []
        for i in zona_evento:
            asiento_zona = Asiento_evento.objects.filter(zona_evento=i.id)
            asiento_evento.append(asiento_zona)
        print(len(asiento_evento))
        return render(request, self.template_name, {'zona_evento': zona_evento, 'asiento_evento': asiento_evento})

class AgregarEvento(View):
    model = Evento
    template_name = 'PanelAdmin/agregarEvento.html'
    form_class= EventoForm
    def get(self, request, *args, **kwargs):
        sala = Sala.objects.all()
        return render(request, self.template_name, {'sala':sala})

    def post(self, request, *args, **kwargs):
        nombre = request.POST.get("nombre")
        imagen = request.FILES["imagen"]
        fecha_hora = request.POST.get("fecha_hora")
        sala = request.POST.get("sala")

        objSala = Sala.objects.get(id=sala)
        print("antes de imagen")
        print(imagen)
        print("despues de imagen")
        objEvento = Evento.objects.create(nombre=nombre,
                                         imagen=imagen,
                                         fecha_hora=fecha_hora,
                                         disponibles=objSala.aforo,
                                         sala=objSala)

        objEvento.save()

        evento = Evento.objects.all().last()
        zona = Zona.objects.filter(sala=sala)
        for i in zona:

            zona_evento = Zona_evento.objects.create(evento=evento,
                                                   zona=i,
                                                   disponibles=i.aforo,
                                                    precio=0)

            zona_evento.save()

            zona_evento_ultima = Zona_evento.objects.all().last()
            asiento = Asiento.objects.filter(zona=i.id)
            for j in asiento:

                asiento_evento = Asiento_evento.objects.create(zona_evento=zona_evento_ultima,
                                                               asiento=j,
                                                               estado=False)
                asiento_evento.save()

        return redirect('asignarPrecioZonaEvento')

"""Necesitamos asignar un precio por zona, en cada evento"""
class AsignarPrecioZonaEvento(View):
    model = Zona_evento
    template_name = 'PanelAdmin/asignarPrecioZonaEvento.html'

    def get(self, request, *args, **kwargs):
        evento = Evento.objects.all().last()
        zonaEvento = Zona_evento.objects.filter(evento = evento)
        return render(request, self.template_name, {'evento':evento, 'zonaEvento':zonaEvento})

    def post(self, request, *args, **kwargs):
        evento = Evento.objects.all().last()
        zonaEvento = Zona_evento.objects.filter(evento=evento)

        for i in zonaEvento:
            precio = request.POST.get(str(i.id))
            i.precio = precio
            i.save()

        return redirect('panelAdmin')

class EditarEvento(UpdateView):
    model = Evento
    fields = '__all__'

    def get_success_url(self, **kwargs):
        return reverse('panelAdmin')

"""Cambiar para que elimine en cascada"""
class EliminarEvento(DeleteView):
    model = Evento
    fields = '__all__'

    def get_success_url(self, **kwargs):
        return reverse('panelAdmin')

class AgregarZonaEvento(CreateView):
    model = Zona_evento
    template_name = 'PanelAdmin/agregarZonaEvento.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse('panelAdmin')

class EditarZonaEvento(UpdateView):
    model = Zona_evento
    fields = '__all__'

    def get_success_url(self, **kwargs):
        return reverse('panelAdmin')

class EliminarZonaEvento(DeleteView):
    model = Zona_evento
    fields = '__all__'

    def get_success_url(self, **kwargs):
        return reverse('panelAdmin')

class AgregarAsientoEvento(CreateView):
    model = Asiento_evento
    template_name = 'PanelAdmin/agregarAsientoEvento.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse('panelAdmin')

class EditarAsientoEvento(UpdateView):
    model = Asiento_evento
    fields = '__all__'

    def get_success_url(self, **kwargs):
        return reverse('panelAdmin')

class EliminarAsientoEvento(DeleteView):
    model = Asiento_evento
    fields = '__all__'

    def get_success_url(self, **kwargs):
        return reverse('panelAdmin')

"""PAYPAL"""
class PaypalConfig(AppConfig):
    name = 'paypal'

class Paypal(TemplateView):
    template_name = 'main/paypal.html'
    def get(self, request):
        """recuperar total y pasarla por parametros"""
        return render(request, self.template_name)
def pago(request):
    """el producto"""
    entrada = Asiento_evento.objects.get(pk=1)
    data = json.loads(request.body)
    order_id = data('orderID')

    detalle = GetOrder().get_order(order_id)
    detalle_precio = float(detalle.result.purchase_units[0].amount.value)
    print(detalle_precio)

    if detalle_precio == entrada.zona_evento.precio:
        trx = CaptureOrder().capture_order(order_id, debug=True)
        pedido = Compra_total(
            id = Asiento_evento.objects.get(pk=1),
            usuario = trx.result.payer.name.given_name,
            fecha_hora = date.today(),
            zona_evento = "",
            total = trx.result.purchase_units[0].payments.captures[0].amount.value
        )

        asiento_comprado = Compra_asiento(
            id = "",
            asiento_evento = Asiento_evento.objects.get(pk=1),
            compra = pedido.id
        )
        pedido.save()
        asiento_comprado.save()

        data = {
            "id": f"{trx.result.id}",
            "nombre_cliente": f"{trx.result.payer.name.given_name}",
            "mensaje": "=D"
        }

        return JsonResponse(data)

    else:
        data = {
            "nombre_cliente": "Error =("
        }

        return JsonResponse(data)

class PaypalClient:
    def __init__(self):
        self.client_id = "AUaptIISTlY2j2l7TOT4NgG_R-ow7ZKZEP-qmTDGmhY5kItHZgk4P-vYLlX1Hr7iVHFoBRMmg-n0vIJD"
        self.client_secret = "EL88ceYkvO1RSMAKzkRUEHdPU4IJtiIDLe_aBJM1s2m88slXIsfJOJRo2JLdJba7uyKKp1sVV0cWPTrn"

        self.environment = SandboxEnvironment(client_id=self.client_id, client_secret=self.client_secret)

        self.client = PayPalHttpClient(self.environment)

    def object_to_json(self, json_data):
        result = {}
        if sys.version_info[0] < 3:
            itr = json_data.__dict__.iteritems()
        else:
            itr = json_data.__dict__.items()
        for key, value in itr:
            if key.startswith("__"):
                continue
            result[key] = self.array_to_json_array(value) if isinstance(value, list) else\
                        self.object_to_json(value) if not self.is_primittive(value) else\
                         value
        return result

    def array_to_json_array(self, json_array):
        result = []
        if isinstance(json_array, list):
            for item in json_array:
                result.append(self.object_to_json(item) if not self.isprimittive(item) \
                              else self.array_to_json_array(item) if isinstance(item, list) else item)
                return result

    def is_primittive(self, data):
        return isinstance(data, str) or isinstance(data, unicode) or isinstance(data, int)


class GetOrder(PaypalClient):
    def get_order(self, order_id):
        request = OrdersGetRequest(order_id)
        response = self.client.execute(request)

# if __name__ == '__main':
#     GetOrder().get_order('REPLACE-WITH-VALID-ORDER-ID')

class CaptureOrder(PaypalClient):
    def capture_order(self, order_id, debug=False):
        request = OrdersCaptureRequest(order_id)
        response = self.client.execute(request)

        return response
# if __name__ == "__main":
#     order_id = ""
#     CaptureOrder().capture_order(order_id, debug=True)
