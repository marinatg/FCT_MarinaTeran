import pytest

from main.models import Sala, Zona, Asiento


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