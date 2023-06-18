from datetime import date, datetime

import pytz
from cffi.backend_ctypes import unicode
from django.contrib.sessions import serializers

from django.db.models import Q, Count, Sum
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, resolve
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView

from main.forms import UnidadesForm, EventoForm, SalaForm
from main.models import *

from django.db import transaction
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import *
from django.contrib.auth import login, logout, authenticate
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from django.core.serializers import serialize

from paypalcheckoutsdk.orders import OrdersGetRequest, OrdersCaptureRequest
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
import sys, json
from reportlab.pdfgen import canvas
from django.http import HttpResponse



# Create your views here.


"""Serializar objetos de la clase Asiento_evento en formato JSON"""
class LazyEncoder(DjangoJSONEncoder):
    """Si el objeto es una instancia de esa clase, devuelve su representación en formato string"""
    def default(self, obj):
        if isinstance(obj, Asiento_evento):
            return str(obj)
        return super().default(obj)

"""Serializar int y float en formato JSON"""
class CustomEncoder(json.JSONEncoder):
    """Si el objeto es de tipo int o float, devuelve su representación en formato string"""
    def default(self, obj):
        if isinstance(obj, int) or isinstance(obj, float):
            return str(obj)
        raise TypeError("No se puede serializar el objeto")

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

                    login(request, user)
                    return redirect('listadoEventos')
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

        compras = Compra_total.objects.filter(usuario=num_user).order_by('id')

        return render(request, self.template_name, {'perfil': perfil, 'compras': compras})

class CompraDetalle(TemplateView):
    template_name = 'main/resumenCompra.html'

    def get(self, request, pk, *args, **kwargs):
        ultimo_pedido = Compra_total.objects.get(id=pk)
        asientos = Compra_asiento.objects.filter(compra=ultimo_pedido.id).order_by('id')

        generar = request.GET.get("pdf", "cero")
        if generar != "cero":
            # Crear la respuesta HTTP con el PDF adjunto
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="entradas.pdf"'

            # Generar el contenido del PDF
            buffer = response
            p = canvas.Canvas(buffer)

            evento_nombre = ultimo_pedido.zona_evento.evento.nombre
            precio = "Total: " + str(ultimo_pedido.total) + " €"
            fecha = "Fecha del evento: " + str(ultimo_pedido.zona_evento.evento.fecha_hora)
            sala = "Sala: " + ultimo_pedido.zona_evento.evento.sala.nombre
            zona = "Zona: " + ultimo_pedido.zona_evento.zona.nombre

            for a in asientos:
                # Añadir título al PDF
                p.setFont('Helvetica-Bold', 32)
                p.drawString(70, 720, evento_nombre)

                # Añadir imagen al PDF
                #image_path = '	http://localhost:8000/main/imagenes/marcadeagua.png'
                image_path = '	http://3.216.41.255:9001/imagenes/main/imagenes/marcadeagua.png'
                p.drawImage(image_path, 490, 750, width=80, height=80)

                # Mas contenido
                #image_path = 'http://localhost:8000/' + str(ultimo_pedido.zona_evento.evento.imagen.url)
                image_path = '	http://3.216.41.255:9001/' + str(ultimo_pedido.zona_evento.evento.imagen.url)
                p.drawImage(image_path, 100, 500, width=350, height=200)

                p.setFont('Helvetica', 27)
                p.drawString(70, 460, precio)

                p.setFont('Helvetica', 17)
                p.drawString(70, 420, fecha)

                p.setFont('Helvetica', 17)
                p.drawString(70, 380, sala)

                #image_path = 'http://localhost:8000/' + str(ultimo_pedido.zona_evento.zona.sala.mapa)
                image_path = 'http://3.216.41.255:9001/imagenes/' + str(ultimo_pedido.zona_evento.zona.sala.mapa)
                p.drawImage(str(image_path), 220, 330, width=100, height=70)

                p.setFont('Helvetica', 27)
                p.drawString(70, 280, zona)

                n = a.asiento_evento.asiento.nombre
                p.setFont('Helvetica-Bold', 30)
                p.drawString(70, 180, n)
                #image_path = 'http://localhost:8000/main/imagenes/QR.png'
                image_path = 'http://3.216.41.255:9001/imagenes/main/imagenes/QR.png'
                p.drawImage(image_path, 250, 130, width=130, height=130)

                p.showPage()

            # Finalizar el PDF

            p.save()

            return response

        return render(request, self.template_name, {'ultimo_pedido': ultimo_pedido, 'asientos': asientos})


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

        ahora = datetime.now(pytz.utc)

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

        return render(request, self.template_name, {'evento':evento, 'busqueda': busqueda, 'disponible': disponible, 'fechaInicio': fechaInicio, 'fechaFin': fechaFin, 'ahora': ahora})

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
        ahora = datetime.now(pytz.utc)
        if evento.fecha_hora < ahora:
            eval = 0
        else:
            eval = 1
        """Ordenar zonas por id"""
        zonas = Zona_evento.objects.filter(evento=pk).order_by('id')
        zonita = zona
        asientos = []
        if zonita:
            if zonita == '1':
                zonita = 1
                asientos = Asiento_evento.objects.filter(zona_evento=zonas[0].id).order_by('id')
            if zonita == '2':
                zonita = 2
                asientos = Asiento_evento.objects.filter(zona_evento=zonas[1].id).order_by('id')
            if zonita == '3':
                zonita = 3
                asientos = Asiento_evento.objects.filter(zona_evento=zonas[2].id).order_by('id')
        else:
            zonita = 1
            asientos = Asiento_evento.objects.filter(zona_evento=zonas[0].id).order_by('id')

        zonaElegida = Zona_evento.objects.get(id=asientos[0].zona_evento.id)
        unidades = request.GET.get("unidades", "0")
        asientosElegidos = []

        if unidades > "0":

            zona = request.GET.get("zonita")
            zona1 = int(zona) - 1
            asientos = Asiento_evento.objects.filter(zona_evento=zonas[zona1].id).order_by('id')
            for i in asientos:
                asientoEvento = request.GET.get(str(i.id), "False")
                if asientoEvento != "False":
                    asientosElegidos.append(i)

            if "asientos_elegidos" in request.session:
                del request.session['asientos_elegidos']
            if "datosCompra" in request.session:
                del request.session['datosCompra']


            unidades = int(request.GET.get("unidades"))
            precio_entrada = float(request.GET.get("precio_entrada"))
            precio_total = float(request.GET.get("precio"))

            data = {
                'unidades': unidades,
                'precio_entrada': precio_entrada,
                'precio_total': precio_total
            }
            json_data = json.dumps(data, cls=CustomEncoder)

            data = serialize('json', asientosElegidos, cls=LazyEncoder)
            request.session['asientos_elegidos'] = data

            request.session['datosCompra'] = json_data

            request.session.save()

            return redirect('paypal')

        return render(request, self.template_name, {'evento': evento, 'perfil': perfil, 'zonas': zonas, 'zonita': zonita, 'asientos': asientos, 'zonaElegida': zonaElegida, 'eval': eval})

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
        return render(request, self.template_name, {'zona': zona, 'asiento': asiento})

class AgregarSala(View):
    model = Sala
    template_name = 'PanelAdmin/agregarrSala.html'
    form_class = SalaForm

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})
    def post(self, request, *args, **kwargs):
        nombre = request.POST.get("nombre")
        imagen = request.FILES["mapa"]
        zona1 = request.POST.get("zona1")
        zona2 = request.POST.get("zona2")
        zona3 = request.POST.get("zona3")
        aforozona1 = request.POST.get("aforozona1")
        aforozona2 = request.POST.get("aforozona2")
        aforozona3 = request.POST.get("aforozona3")

        aforo_total = int(aforozona1) + int(aforozona2) + int(aforozona3)

        objSala = Sala.objects.create(nombre=nombre,
                                        mapa=imagen,
                                        aforo=aforo_total)
        objSala.save()

        sala = Sala.objects.all().last()

        zona_uno = Zona.objects.create(sala=sala,
                                        nombre=zona1,
                                        aforo=aforozona1)
        zona_uno.save()
        zona_dos = Zona.objects.create(sala=sala,
                                       nombre=zona2,
                                       aforo=aforozona2)
        zona_dos.save()
        zona_tres = Zona.objects.create(sala=sala,
                                        nombre=zona3,
                                        aforo=aforozona3)
        zona_tres.save()

        zonas = Zona.objects.filter(sala=sala.id)

        cont = 0
        aforo = 0
        for z in zonas:
            cont = cont + 1
            if cont == 1:
                letra_asiento = "A"
                aforo = int(aforozona1)
            if cont == 2:
                letra_asiento = "B"
                aforo = int(aforozona2)
            if cont == 3:
                letra_asiento = "C"
                aforo = int(aforozona3)

            for i in range(0, aforo):
                if i < 10:
                    letra_dos = "0"
                else:
                    letra_dos = ""

                asiento = Asiento.objects.create(zona = z,
                                                 nombre = letra_asiento + letra_dos + str(i))
                asiento.save()

        return redirect('panelAdmin')


class EditarSala(UpdateView):
    model = Sala
    fields = ['nombre', 'mapa']

    def get_success_url(self, **kwargs):
        return reverse('panelAdmin')

class EliminarSala(DeleteView):
    model = Sala
    fields = '__all__'
    def post(self, request, *args, **kwargs):
        for key, value in kwargs.items():
            idSala = value
            evento = Evento.objects.filter(sala=idSala)
            for ev in evento:
                r_zonasE = Zona_evento.objects.filter(evento=ev.id).order_by('id')
                for y in r_zonasE:
                    zonasE = Zona_evento.objects.get(id=y.id)
                    r_asientosE = Asiento_evento.objects.filter(zona_evento=zonasE.id).order_by('id')
                    """Recorro las zonas y busco las compras que la contienen para eliminarlas"""
                    compra_evento = Compra_total.objects.filter(zona_evento=y).order_by('id')
                    for c in compra_evento:
                        """Lo mismo con compra_asiento..."""
                        entradas = Compra_asiento.objects.filter(compra=c).order_by('id')
                        for e in entradas:
                            entradas.delete()
                    compra_evento.delete()
                    for p in r_asientosE:
                        asientos = Asiento_evento.objects.get(id=p.id)
                        asientos.delete()
                    zonasE.delete()
                ev.delete()

        sala = Sala.objects.get(id=idSala)
        r_zonas = Zona.objects.filter(sala=sala.id).order_by('id')
        for z in r_zonas:
            zonas = Zona.objects.get(id=z.id)
            r_asientos = Asiento.objects.filter(zona=zonas.id).order_by('id')
            for a in r_asientos:
                asientos = Asiento.objects.get(id=a.id)
                asientos.delete()
            zonas.delete()
        sala.delete()

        return redirect('panelAdmin')



class AdministrarEvento(View):
    model = Evento
    template_name = 'PanelAdmin/administrarEvento.html'

    def get(self, request, pk, *args, **kwargs):
        zona_evento = Zona_evento.objects.filter(evento=pk)
        asiento_evento = []
        for i in zona_evento:
            asiento_zona = Asiento_evento.objects.filter(zona_evento=i.id)
            asiento_evento.append(asiento_zona)
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
        objEvento = Evento.objects.create(nombre=nombre,
                                         imagen=imagen,
                                         fecha_hora=fecha_hora,
                                         disponibles=objSala.aforo,
                                         sala=objSala)

        objEvento.save()

        evento = Evento.objects.all().last()
        zona = Zona.objects.filter(sala=sala).order_by('id')
        for i in zona:

            zona_evento = Zona_evento.objects.create(evento=evento,
                                                   zona=i,
                                                   disponibles=i.aforo,
                                                    precio=0)

            zona_evento.save()

            zona_evento_ultima = Zona_evento.objects.all().last()
            asiento = Asiento.objects.filter(zona=i.id).order_by('id')
            for j in asiento:

                asiento_evento = Asiento_evento.objects.create(zona_evento=zona_evento_ultima,
                                                               asiento=j,
                                                               estado=False)
                asiento_evento.save()

        return redirect('asignarPrecioZonaEvento')

class AsignarPrecioZonaEvento(View):
    model = Zona_evento
    template_name = 'PanelAdmin/asignarPrecioZonaEvento.html'

    def get(self, request, *args, **kwargs):
        evento = Evento.objects.all().last()
        zonaEvento = Zona_evento.objects.filter(evento = evento)
        return render(request, self.template_name, {'evento':evento, 'zonaEvento':zonaEvento})

    def post(self, request, *args, **kwargs):
        evento = Evento.objects.all().last()
        zonaEvento = Zona_evento.objects.filter(evento=evento).order_by('id')

        for i in zonaEvento:
            precio = request.POST.get(str(i.id))
            i.precio = precio
            i.save()

        return redirect('panelAdmin')

class EditarEvento(UpdateView):
    model = Evento
    fields = ['nombre', 'imagen', 'fecha_hora']

    def get_success_url(self, **kwargs):
        return reverse('panelAdmin')

class EliminarEvento(DeleteView):
    model = Evento
    fields = '__all__'

    def post(self, request, *args, **kwargs):
        for key, value in kwargs.items():
            idEvento = value
            print(idEvento)
        evento = Evento.objects.get(id=idEvento)
        r_zonas = Zona_evento.objects.filter(evento=evento.id).order_by('id')
        for z in r_zonas:
            zonas = Zona_evento.objects.get(id=z.id)
            r_asientos = Asiento_evento.objects.filter(zona_evento=zonas.id).order_by('id')
            """Recorro las zonas y busco las compras que la contienen para eliminarlas"""
            compra_evento = Compra_total.objects.filter(zona_evento=z).order_by('id')
            for c in compra_evento:
                """Lo mismo con compra_asiento..."""
                entradas = Compra_asiento.objects.filter(compra=c).order_by('id')
                for e in entradas:
                    entradas.delete()
            compra_evento.delete()
            for a in r_asientos:
                asientos = Asiento_evento.objects.get(id=a.id)
                asientos.delete()
            zonas.delete()
        evento.delete()

        return redirect('panelAdmin')



"""PAYPAL"""


class Paypal(TemplateView):
    template_name = 'main/paypal.html'
    def get(self, request):

        """recuperar total y pasarla por parametros"""
        if 'datosCompra' in request.session:
            entradas = request.session['datosCompra']

            data = json.loads(entradas)
            total = data['precio_total']

        return render(request, self.template_name, {'total': total})

    def post(self, request):

        return redirect('resumenCompra')

def pago(request):
    asientoEvento = []
    if 'asientos_elegidos' in request.session:
        items = request.session['asientos_elegidos']
        for obj in serializers.deserialize('json', items):
            asientoEvento.append(obj.object)
    if 'datosCompra' in request.session:
        entradas = request.session['datosCompra']
        data = json.loads(entradas)
        unidades = data['unidades']
        precio_entrada = data['precio_entrada']
        precio_total = data['precio_total']
    data = json.loads(request.body)
    order_id = data['orderID']
    detalle = GetOrder().get_order(order_id)
    detalle_precio = float(detalle.result.purchase_units[0].amount.value)

    user = request.user
    num_user = user.id
    usuario = User.objects.get(id = request.user.id)

    if detalle_precio == precio_total:
        trx = CaptureOrder().capture_order(order_id, debug=True)
        pedido = Compra_total.objects.create(
            usuario = usuario,
            fecha_hora = datetime.now(),
            zona_evento = asientoEvento[0].zona_evento,
            total = precio_total
        )
        pedido.save()
        ultimo_pedido = Compra_total.objects.all().last()
        """Restar numero de asientos comprados, de los disponibles en evento y zona"""
        zonaEv = Zona_evento.objects.get(id=ultimo_pedido.zona_evento.id)
        evento = Evento.objects.get(id=zonaEv.evento.id)
        zonaEv.disponibles = zonaEv.disponibles - unidades
        evento.disponibles = evento.disponibles - unidades
        zonaEv.save()
        evento.save()
        for a in asientoEvento:
            asiento_comprado = Compra_asiento.objects.create(
                asiento_evento = a,
                compra = ultimo_pedido
            )

            asiento_comprado.save()
            """Asigno el asiento al usuario y lo inhabilito(ya está comprado)"""
            asiento_reserva = Asiento_evento.objects.get(id=a.id)
            asiento_reserva.usuario = usuario
            asiento_reserva.estado = True
            asiento_reserva.save()

        data = {
            "mensaje": "Correcto"
        }

        return JsonResponse(data)

    else:
        data = {
            "mensaje": "Error en la compra"
        }

        return JsonResponse(data)

class ResumenCompra(TemplateView):
    template_name = 'main/resumenCompra.html'
    def get(self, request):
        ultimo_pedido = Compra_total.objects.filter(usuario=request.user).last()
        asientos = Compra_asiento.objects.filter(compra = ultimo_pedido.id).order_by('id')

        generar = request.GET.get("pdf", "cero")
        if generar != "cero":
            # Crear la respuesta HTTP con el PDF adjunto
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="entradas.pdf"'

            # Generar el contenido del PDF
            buffer = response
            p = canvas.Canvas(buffer)

            evento_nombre = ultimo_pedido.zona_evento.evento.nombre
            precio = "Total: " + str(ultimo_pedido.total) + " €"
            fecha = "Fecha del evento: " + str(ultimo_pedido.zona_evento.evento.fecha_hora)
            sala = "Sala: " + ultimo_pedido.zona_evento.evento.sala.nombre
            zona = "Zona: " + ultimo_pedido.zona_evento.zona.nombre

            for a in asientos:
                # Añadir título al PDF
                p.setFont('Helvetica-Bold', 32)
                p.drawString(70, 720, evento_nombre)

                # Añadir imagen al PDF
                #image_path = 'http://localhost:8000/main/imagenes/marcadeagua.png'
                image_path = 'http://3.216.41.255:9001/imagenes/main/imagenes/marcadeagua.png'
                p.drawImage(image_path, 490, 750, width=80, height=80)

                # Mas contenido
                #image_path = 'http://localhost:8000/' + str(ultimo_pedido.zona_evento.evento.imagen.url)
                image_path = 'http://3.216.41.255:9001/' + str(ultimo_pedido.zona_evento.evento.imagen.url)
                p.drawImage(image_path, 100, 500, width=350, height=200)

                p.setFont('Helvetica', 27)
                p.drawString(70, 460, precio)

                p.setFont('Helvetica', 17)
                p.drawString(70, 420, fecha)

                p.setFont('Helvetica', 17)
                p.drawString(70, 380, sala)

                #image_path = 'http://localhost:8000/' + str(ultimo_pedido.zona_evento.zona.sala.mapa)
                image_path = 'http://3.216.41.255:9001/imagenes/' + str(ultimo_pedido.zona_evento.zona.sala.mapa)
                p.drawImage(str(image_path), 220, 330, width=100, height=70)

                p.setFont('Helvetica', 27)
                p.drawString(70, 280, zona)

                n = a.asiento_evento.asiento.nombre
                p.setFont('Helvetica-Bold', 30)
                p.drawString(70, 180, n)
                #image_path = 'http://localhost:8000/main/imagenes/QR.png'
                image_path = 'http://3.216.41.255:9001/imagenes/main/imagenes/QR.png'
                p.drawImage(image_path, 250, 130, width=130, height=130)

                p.showPage()

            # Finalizar el PDF

            p.save()

            return response

        return render(request, self.template_name, {'ultimo_pedido': ultimo_pedido, 'asientos': asientos})

class PaypalClient:
    """Constructor de la clase PaypalClient.
        Inicializa las credenciales de cliente y el entorno de sandbox de PayPal."""
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
        """Devuelve True si el dato es una cadena de texto (str), unicode o entero (int).
            Devuelve False en caso contrario."""
        return isinstance(data, str) or isinstance(data, unicode) or isinstance(data, int)


class GetOrder(PaypalClient):
    """Obtiene una orden específica de PayPal.
        Recibe un ID de orden y realiza una solicitud a la API de PayPal para obtener los detalles de esa orden.
        Devuelve la respuesta obtenida."""
    def get_order(self, order_id):
        request = OrdersGetRequest(order_id)
        response = self.client.execute(request)
        return response
# if __name__ == '__main':
#     GetOrder().get_order('REPLACE-WITH-VALID-ORDER-ID')

class CaptureOrder(PaypalClient):
    """Captura una orden específica de PayPal.
        Recibe un ID de orden y realiza una solicitud a la API de PayPal para capturar dicha orden.
        Devuelve la respuesta obtenida.
        :param order_id: El ID de la orden a capturar.
        :param debug: Bandera opcional para activar el modo de depuración. Por defecto, es False.
        :return: La respuesta obtenida al capturar la orden."""
    def capture_order(self, order_id, debug=False):
        request = OrdersCaptureRequest(order_id)
        response = self.client.execute(request)

        return response
# if __name__ == "__main":
#     order_id = ""
#     CaptureOrder().capture_order(order_id, debug=True)

"""INFORMES"""

class Top5clientes(TemplateView):
    def get(self, request, *args, **kwargs):
        cliente = User.objects.annotate(nCompras=Count('compra_total__id'),nTotal=Sum('compra_total__total')).order_by('-nCompras')[:5]

        return render(request, 'PanelAdmin/top5clientes.html', {'cliente': cliente})

class ComprasPorUsuario(ListView):
    model = Compra_total
    fields = '__all__'
    template_name = 'PanelAdmin/comprasPorUsuario.html'
    def get(self, request, *args, **kwargs):
        compras = Compra_total.objects.all()
        busqueda = request.GET.get("buscar")
        print(busqueda)
        if busqueda:
            usuario = User.objects.filter(username__icontains=busqueda)
            compras = Compra_total.objects.filter(usuario__username__contains=busqueda)
            print(compras)

        return render(request, 'PanelAdmin/comprasPorUsuario.html', {'compras': compras})
