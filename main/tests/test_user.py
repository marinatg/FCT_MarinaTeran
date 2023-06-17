import pytest

from django.test import TestCase, Client

from django.contrib.auth.models import User
from main.tests.factories import UsuarioAdminFactory, UsuarioComunFactory

class UsuarioTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.common_user = UsuarioComunFactory.create()
        self.superuser = UsuarioAdminFactory.create()

    def test_common_user_creation(self):
        self.assertEqual(self.common_user.is_active, True)
        self.assertEqual(self.common_user.is_staff, False)
        self.assertEqual(self.common_user.is_superuser, False)

    def test_suerpuser_creation(self):
        self.assertEqual(self.superuser.is_staff, True)
        self.assertEqual(self.superuser.is_superuser, True)

    def test_login(self):
        self.common_user.set_password('marina')
        self.common_user.save()
        response = self.client.login(username='marina_comun', password='marina')
        self.assertEqual(response, True)

    def test_login_fail(self):
        self.common_user.set_password('marina')
        self.common_user.save()
        response = self.client.login(username='marina_comun', password='marina1')
        self.assertEqual(response, False)

    def test_users_list(self):
        self.superuser.set_password('marina')
        self.superuser.save()
        self.client.login(username='marina_superuser', password='marina')
        response = self.client.get('/admin/auth/user/',
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        #self.assertEquals(len(response.json()), 1)