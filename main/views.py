from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import *
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView

from main.forms import UnidadesForm
from main.models import *


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
        metodo_pago = Metodo_pago.objects.filter(usuario_id=num_user)
        "compras = self.model.objects.filter(perfil_id=perfil[0].id)"
        "pago = Metodo_pago.objects.filter(perfil_id=perfil[0].id)"

        return render(request, self.template_name, {'perfil': perfil, 'metodo_pago': metodo_pago})

class AgregarPerfil(CreateView):
    model = Perfil
    template_name = 'main/agregarPerfil.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse('perfil')

class EditarPerfil(UpdateView):
    model = Perfil
    fields = '__all__'

    def get_success_url(self, **kwargs):
        return reverse('perfil')

class EliminarPerfil(DeleteView):
    model = Perfil
    fields = '__all__'
    def get_success_url(self, *args, **kwargs):
        return reverse('perfil')

class AgregarMetodoPago(CreateView):
    model = Metodo_pago
    template_name = 'main/agregarMetodoPago.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse('perfil')

class EditarMetodoPago(UpdateView):
    model = Metodo_pago
    fields = '__all__'

    def get_success_url(self, **kwargs):
        return reverse('perfil')

class EliminarMetodoPago(DeleteView):
    model = Metodo_pago
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

        return render(request,self.template_name, {'evento':evento, 'busqueda': busqueda, 'disponible': disponible, 'fechaInicio': fechaInicio, 'fechaFin': fechaFin})

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
        print("textito antes " + unidades)
        asientosElegidos = []
        if unidades > "0":
            print("mayor que 0")
            print(asientos)
            for i in asientos:
                asientoEvento = request.GET.get(str(i.id), "False")
                print(i.id)
                print(asientoEvento)
                if asientoEvento != "False":
                    asientosElegidos.append(asientoEvento)
                    print(asientosElegidos)
        else:
            print("cero")

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

class AgregarEvento(CreateView):
    model = Evento
    template_name = 'PanelAdmin/agregarEvento.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse('panelAdmin')




