import factory
from django.contrib.auth.models import User

class UsuarioComunFactory(factory.Factory):
    class Meta:
        model = User

    first_name = "Marina"
    username = "marina_comun"
    email = 'usuarioprueba@gmail.com'
    is_staff = False


class UsuarioAdminFactory(factory.Factory):
    class Meta:
        model = User

    first_name = "Marina"
    username = "marina_superuser"
    is_staff = True
    is_superuser = True


class UsuarioStaffFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = "Marina"
    username = "marina_staff"
    email = 'usuarioprueba@gmail.com'
    is_staff = True