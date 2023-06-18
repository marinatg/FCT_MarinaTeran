from django.test import TestCase
from django.contrib.auth.models import User
from main.models import Sala, Zona, Asiento, Evento, Zona_evento, Asiento_evento, Compra_total, Compra_asiento
from datetime import datetime, date
import pytz

class MainAppTestCase(TestCase):
    def setUp(self):
        self.sala_creation = Sala.objects.create(
            nombre="kghuytrdl",
            mapa="main/imagenes/logo2.png",
            aforo="100"
        )

    def test_sala_creation(self):
        self.assertEqual(self.sala_creation.nombre, "kghuytrdl")

    def setUp(self):
        self.sala_creation = Sala.objects.create(
            nombre="kghuytrdl",
            mapa="main/imagenes/logo2.png",
            aforo="100"
        )
        self.zona_creation = Zona.objects.create(
            nombre="patio",
            aforo="50",
            sala=self.sala_creation
        )

    def test_zona_creation(self):
        self.assertEqual(self.zona_creation.nombre, "patio")

    def setUp(self):
        self.sala_creation = Sala.objects.create(
            nombre="kghuytrdl",
            mapa="main/imagenes/logo2.png",
            aforo="100"
        )
        self.zona_creation = Zona.objects.create(
            nombre="patio",
            aforo="50",
            sala=self.sala_creation
        )
        self.asiento_creation = Asiento.objects.create(
            nombre="A00",
            zona=self.zona_creation
        )

    def test_asiento_creation(self):
        self.assertEqual(self.asiento_creation.nombre, "A00")

    def setUp(self):
        self.sala_creation = Sala.objects.create(
            nombre="kghuytrdl",
            mapa="main/imagenes/logo2.png",
            aforo="100"
        )
        self.evento_creation = Evento.objects.create(
            nombre="miEvento",
            imagen="main/imagenes/logo2.png",
            fecha_hora=datetime.now(pytz.utc),
            disponibles=50,
            sala=self.sala_creation
        )

    def test_evento_creation(self):
        self.assertEqual(self.evento_creation.nombre, "miEvento")

    def setUp(self):
        self.sala_creation = Sala.objects.create(
            nombre="kghuytrdl",
            mapa="main/imagenes/logo2.png",
            aforo="100"
        )
        self.evento_creation = Evento.objects.create(
            nombre="miEvento",
            imagen="main/imagenes/logo2.png",
            fecha_hora=datetime.now(pytz.utc),
            disponibles=50,
            sala=self.sala_creation
        )
        self.zona_creation = Zona.objects.create(
            nombre="patio",
            aforo="50",
            sala=self.sala_creation
        )
        self.zona_evento_creation = Zona_evento.objects.create(
            disponibles=50,
            precio=5,
            evento=self.evento_creation,
            zona=self.zona_creation
        )

    def test_zona_evento_creation(self):
        self.assertEqual(self.zona_evento_creation.disponibles, 50)

    def setUp(self):
        self.common_user_creation = User.objects.create(
            username='dasdas',
            email='asdasda@gmail.com',
            first_name='wegw gwgwe',
            password='12345',
            is_staff=False
        )

    def test_common_user_creation(self):
        self.assertEqual(self.common_user_creation.username, 'dasdas')

    def setUp(self):
        self.sala_creation = Sala.objects.create(
            nombre="kghuytrdl",
            mapa="main/imagenes/logo2.png",
            aforo="100"
        )
        self.evento_creation = Evento.objects.create(
            nombre="miEvento",
            imagen="main/imagenes/logo2.png",
            fecha_hora=datetime.now(pytz.utc),
            disponibles=50,
            sala=self.sala_creation
        )
        self.zona_creation = Zona.objects.create(
            nombre="patio",
            aforo="50",
            sala=self.sala_creation
        )
        self.asiento_creation = Asiento.objects.create(
            nombre="A00",
            zona=self.zona_creation
        )
        self.zona_evento_creation = Zona_evento.objects.create(
            disponibles=50,
            precio=5,
            evento=self.evento_creation,
            zona=self.zona_creation
        )
        self.common_user_creation = User.objects.create(
            username='dasdas',
            email='asdasda@gmail.com',
            first_name='wegw gwgwe',
            password='12345',
            is_staff=False
        )
        self.asiento_evento_creation = Asiento_evento.objects.create(
            estado=False,
            zona_evento=self.zona_evento_creation,
            asiento=self.asiento_creation,
            usuario=self.common_user_creation
        )

    def test_asiento_evento_creation(self):
        self.assertEqual(self.asiento_evento_creation.estado, False)

    def setUp(self):
        self.sala_creation = Sala.objects.create(
            nombre="kghuytrdl",
            mapa="main/imagenes/logo2.png",
            aforo="100"
        )
        self.evento_creation = Evento.objects.create(
            nombre="miEvento",
            imagen="main/imagenes/logo2.png",
            fecha_hora=datetime.now(pytz.utc),
            disponibles=50,
            sala=self.sala_creation
        )
        self.zona_creation = Zona.objects.create(
            nombre="patio",
            aforo="50",
            sala=self.sala_creation
        )
        self.asiento_creation = Asiento.objects.create(
            nombre="A00",
            zona=self.zona_creation
        )
        self.zona_evento_creation = Zona_evento.objects.create(
            disponibles=50,
            precio=5,
            evento=self.evento_creation,
            zona=self.zona_creation
        )
        self.common_user_creation = User.objects.create(
            username='dasdas',
            email='asdasda@gmail.com',
            first_name='wegw gwgwe',
            password='12345',
            is_staff=False
        )
        self.asiento_evento_creation = Asiento_evento.objects.create(
            estado=False,
            zona_evento=self.zona_evento_creation,
            asiento=self.asiento_creation,
            usuario=self.common_user_creation
        )
        self.compra_total_creation = Compra_total.objects.create(
            fecha_hora=datetime.now(pytz.utc),
            total=1,
            usuario=self.common_user_creation,
            zona_evento=self.zona_evento_creation
        )

    def test_compra_total_creation(self):
        self.assertEqual(self.compra_total_creation.total, 1)

    def setUp(self):
        self.sala_creation = Sala.objects.create(
            nombre="kghuytrdl",
            mapa="main/imagenes/logo2.png",
            aforo="100"
        )
        self.evento_creation = Evento.objects.create(
            nombre="miEvento",
            imagen="main/imagenes/logo2.png",
            fecha_hora=datetime.now(pytz.utc),
            disponibles=50,
            sala=self.sala_creation
        )
        self.zona_creation = Zona.objects.create(
            nombre="patio",
            aforo="50",
            sala=self.sala_creation
        )
        self.asiento_creation = Asiento.objects.create(
            nombre="A00",
            zona=self.zona_creation
        )
        self.zona_evento_creation = Zona_evento.objects.create(
            disponibles=50,
            precio=5,
            evento=self.evento_creation,
            zona=self.zona_creation
        )
        self.common_user_creation = User.objects.create(
            username='dasdas',
            email='asdasda@gmail.com',
            first_name='wegw gwgwe',
            password='12345',
            is_staff=False
        )
        self.asiento_evento_creation = Asiento_evento.objects.create(
            estado=False,
            zona_evento=self.zona_evento_creation,
            asiento=self.asiento_creation,
            usuario=self.common_user_creation
        )
        self.compra_total_creation = Compra_total.objects.create(
            fecha_hora=datetime.now(pytz.utc),
            total=1,
            usuario=self.common_user_creation,
            zona_evento=self.zona_evento_creation
        )
        self.compra_asiento_creation = Compra_asiento.objects.create(
            compra=self.compra_total_creation,
            asiento_evento=self.asiento_evento_creation
        )

    def test_compra_asiento_creation(self):
        self.assertEqual(self.compra_asiento_creation.compra, self.compra_total_creation)

