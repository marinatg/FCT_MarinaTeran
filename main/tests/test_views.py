from datetime import datetime
from io import BytesIO
import pytz
from django.test import TestCase

from django.test import TestCase, Client
from django.contrib.auth.models import User

from main.models import Sala, Evento
from main.tests.factories import UsuarioAdminFactory, UsuarioComunFactory


"""Verifica la creación de sala y evento, que la respuesta es correcta 
en los métodos get y post de cada una de las vistas, y que redirige de forma correcta en cada paso.
Tambien se prueba la carga de evento detalle, una vez hecho lo anterior.
Que se listan bien los eventos y el detalle de la sala y el evento."""
class MainViewTests(TestCase):

    def test_welcome(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

class SalaEventoTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.common_user = UsuarioComunFactory.create()
        self.superuser = UsuarioAdminFactory.create()

    def test_sala_evento(self):
        self.superuser.set_password('marina')
        self.superuser.save()
        self.client.login(username='marina_superuser', password='marina')
        print('USUARIO LOGUEADO.')
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/PanelAdmin/panelAdmin/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/PanelAdmin/agregarSala/')
        self.assertEqual(response.status_code, 200)
        img4 = BytesIO(
        b"GIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00"
        b"\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01\x00\x00")
        img4.name = "myimage.gif"
        response = self.client.post('/PanelAdmin/agregarSala/',
                                    {
                                        'nombre': 'Misala',
                                        'mapa': img4,
                                        'zona1': 'Pista',
                                        'zona2': 'Grada 1',
                                        'zona3': 'Grada 2',
                                        'aforozona1': 30,
                                        'aforozona2': 20,
                                        'aforozona3': 10,
                                    }
                                )
        img4.close()
        print('SALA CREADA')
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/PanelAdmin/administrarSala/1')
        self.assertEqual(response.status_code, 200)


        response = self.client.get('/PanelAdmin/agregarEvento/')
        self.assertEqual(response.status_code, 200)
        img2= BytesIO(
            b"GIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00"
            b"\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01\x00\x00")
        img2.name = "myimage.gif"
        sala = Sala.objects.all().last()
        response = self.client.post('/PanelAdmin/agregarEvento/',
                                    {
                                        'nombre': 'MiEvento',
                                        'imagen': img2,
                                        'fecha_hora': datetime.now(pytz.utc),
                                        'sala': sala.id,
                                    }
                                    )
        img2.close()
        print('EVENTO CREADO')
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/PanelAdmin/administrarEvento/1')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
        evento = Evento.objects.all().last()
        response = self.client.get('/main/eventoDetalle/' + str(evento.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['evento'].nombre, 'MiEvento')

        """Editar sala"""
        response = self.client.get('/PanelAdmin/editarSala/' + str(sala.id))
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/PanelAdmin/editarSala/' + str(sala.id),
                                    {
                                        'nombre': 'Tusala',
                                    }
                                )
        print('SALA EDITADA')
        self.assertEqual(response.status_code, 302)
        """Editar evento"""
        response = self.client.get('/PanelAdmin/editarEvento/' + str(evento.id))
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/PanelAdmin/editarEvento/' + str(evento.id),
                                    {
                                        'nombre': 'TuEvento',
                                    }
                                    )
        print('EVENTO EDITADO:')
        print(response.context['evento'])
        self.assertEqual(response.status_code, 200)

        """Eliminar evento"""
        response = self.client.post('/PanelAdmin/eliminarEvento/' + str(evento.id))
        self.assertEqual(response.status_code, 302)

        """Eliminar sala"""
        response = self.client.post('/PanelAdmin/eliminarSala/' + str(sala.id))
        self.assertEqual(response.status_code, 302)

        """Compruebo que se han eliminado correctamente"""
        response = self.client.get('/PanelAdmin/panelAdmin/')
        print('SALA ELIMINADA: ')
        print(response.context['sala'])
        print('EVENTO ELIMINADO: ')
        print(response.context['evento'])
        self.assertEqual(response.status_code, 200)
