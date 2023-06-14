import pytest

from main.models import Sala

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
