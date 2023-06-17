from datetime import datetime, date

import pytest
import pytz

from main.models import Sala, Zona, Asiento, Evento, Zona_evento, Asiento_evento, Compra_total, Compra_asiento
from main.tests.test_user import *

@pytest.fixture
def sala_creation():
    return Sala(
                nombre="kghuytrdl",
                mapa="main/imagenes/logo2.png",
                aforo="100"
            )

@pytest.mark.django_db
def test_sala_creation(sala_creation):
    sala_creation.save()
    assert sala_creation.nombre == "kghuytrdl"

@pytest.fixture
def zona_creation():
    return Zona(
                nombre="patio",
                aforo="50"
            )

@pytest.mark.django_db
def test_zona_creation(sala_creation, zona_creation):
    sala_creation.save()
    zona_creation.sala = sala_creation
    zona_creation.save()
    assert zona_creation.nombre == "patio"

@pytest.fixture
def asiento_creation():
    return Asiento(
                nombre="A00",
            )

@pytest.mark.django_db
def test_asiento_creation(sala_creation, zona_creation, asiento_creation):
    sala_creation.save()
    zona_creation.sala = sala_creation
    zona_creation.save()
    asiento_creation.zona = zona_creation
    asiento_creation.save()
    assert asiento_creation.nombre == "A00"

"""--------"""

@pytest.fixture
def evento_creation():
    return Evento(
                nombre="miEvento",
                imagen="main/imagenes/logo2.png",
                fecha_hora = datetime.now(pytz.utc),
                disponibles = 50,
            )

@pytest.mark.django_db
def test_evento_creation(sala_creation, evento_creation):
    sala_creation.save()
    evento_creation.sala = sala_creation
    evento_creation.save()

    assert evento_creation.nombre == "miEvento"

@pytest.fixture
def zona_evento_creation():
    return Zona_evento(
                disponibles = 50,
                precio = 5
            )

@pytest.mark.django_db
def test_zona_evento_creation(sala_creation, evento_creation, zona_creation, zona_evento_creation):
    sala_creation.save()
    evento_creation.sala = sala_creation
    evento_creation.save()
    zona_creation.sala = sala_creation
    zona_creation.save()
    zona_evento_creation.evento = evento_creation
    zona_evento_creation.zona = zona_creation
    zona_evento_creation.save()

    assert zona_evento_creation.disponibles == 50

@pytest.fixture
def common_user_creation():
    return User(
        username='dasdas',
        email='asdasda@gmail.com',
        first_name='wegw gwgwe',
        password='12345',
        is_staff=False
    )
@pytest.mark.django_db
def test_common_user_creation(common_user_creation):
    common_user_creation.save()
    assert common_user_creation.username == 'dasdas'

@pytest.fixture
def asiento_evento_creation():
    return Asiento_evento(
        estado = False
    )

@pytest.mark.django_db
def test_asiento_evento_creation(sala_creation, evento_creation, zona_creation, asiento_creation, zona_evento_creation, common_user_creation, asiento_evento_creation):
    sala_creation.save()
    evento_creation.sala = sala_creation
    evento_creation.save()
    zona_creation.sala = sala_creation
    zona_creation.save()
    zona_evento_creation.evento = evento_creation
    zona_evento_creation.zona = zona_creation
    zona_evento_creation.save()
    asiento_creation.zona = zona_creation
    asiento_creation.save()

    asiento_evento_creation.zona_evento = zona_evento_creation
    asiento_evento_creation.asiento = asiento_creation
    common_user_creation.save()
    asiento_evento_creation.usuario = common_user_creation
    asiento_evento_creation.save()

    assert asiento_evento_creation.estado == False

@pytest.fixture
def compra_total_creation():
    return Compra_total(
        fecha_hora = datetime.now(pytz.utc),
        total = 1
    )

@pytest.mark.django_db
def test_compra_total_creation(sala_creation, evento_creation, zona_creation, asiento_creation, zona_evento_creation, common_user_creation, asiento_evento_creation, compra_total_creation):
    sala_creation.save()
    evento_creation.sala = sala_creation
    evento_creation.save()
    zona_creation.sala = sala_creation
    zona_creation.save()
    zona_evento_creation.evento = evento_creation
    zona_evento_creation.zona = zona_creation
    zona_evento_creation.save()
    asiento_creation.zona = zona_creation
    asiento_creation.save()
    asiento_evento_creation.zona_evento = zona_evento_creation
    asiento_evento_creation.asiento = asiento_creation
    common_user_creation.save()
    asiento_evento_creation.usuario = common_user_creation
    asiento_evento_creation.save()

    compra_total_creation.usuario = common_user_creation
    compra_total_creation.zona_evento = zona_evento_creation
    compra_total_creation.save()

    assert compra_total_creation.total == 1

@pytest.fixture
def compra_asiento_creation():
    return Compra_asiento()

@pytest.mark.django_db
def test_compra_asiento_creation(sala_creation, evento_creation, zona_creation, asiento_creation, zona_evento_creation, common_user_creation, asiento_evento_creation, compra_total_creation, compra_asiento_creation):
    sala_creation.save()
    evento_creation.sala = sala_creation
    evento_creation.save()
    zona_creation.sala = sala_creation
    zona_creation.save()
    zona_evento_creation.evento = evento_creation
    zona_evento_creation.zona = zona_creation
    zona_evento_creation.save()
    asiento_creation.zona = zona_creation
    asiento_creation.save()
    asiento_evento_creation.zona_evento = zona_evento_creation
    asiento_evento_creation.asiento = asiento_creation
    common_user_creation.save()
    asiento_evento_creation.usuario = common_user_creation
    asiento_evento_creation.save()
    compra_total_creation.usuario = common_user_creation
    compra_total_creation.zona_evento = zona_evento_creation
    compra_total_creation.save()

    compra_asiento_creation.asiento_evento = asiento_evento_creation
    compra_asiento_creation.compra = compra_total_creation
    compra_asiento_creation.save()

    assert compra_asiento_creation.compra == compra_total_creation

    @pytest.fixture
    def perfil_creation():
        return Sala(
            nombre= "Paquito",
            dni = "00000000R",
            fecha_nac = date.today(),
            direccion = "calle solito",
        )

    @pytest.mark.django_db
    def test_perfil_creation(common_user_creation, perfil_creation):
        common_user_creation.save()
        perfil_creation.usuario = common_user_creation
        perfil_creation.save()
        assert perfil_creation.nombre == "Paquito"

