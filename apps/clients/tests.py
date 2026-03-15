from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.clients.models import Client

User = get_user_model()


class ClientSearchTests(TestCase):
    def setUp(self):
        self.operator = User.objects.create_user(
            username='operator1',
            password='Test12345',
            role=User.Role.OPERATOR
        )

        Client.objects.create(
            noms='KOUASSI',
            prenoms='Jean',
            date_naissance='2000-01-01',
            lieu_naissance='Abidjan',
            lieu_enrolement='Yopougon',
            rangement='A-01'
        )

        Client.objects.create(
            noms='KONE',
            prenoms='Awa',
            date_naissance='1998-02-10',
            lieu_naissance='Bouaké',
            lieu_enrolement='Cocody',
            rangement='B-02'
        )

    def test_search_requires_login(self):
        response = self.client.get(reverse('client_search'))
        self.assertEqual(response.status_code, 302)

    def test_operator_can_access_search(self):
        self.client.login(username='operator1', password='Test12345')
        response = self.client.get(reverse('client_search'))
        self.assertEqual(response.status_code, 200)

    def test_search_by_name(self):
        self.client.login(username='operator1', password='Test12345')
        response = self.client.get(reverse('client_search'), {'noms': 'KOUASSI'})
        self.assertEqual(response.status_code, 200)

        clients = response.context['clients']
        self.assertEqual(clients.count(), 1)
        self.assertEqual(clients[0].noms, 'KOUASSI')

    def test_search_by_prenoms(self):
        self.client.login(username='operator1', password='Test12345')
        response = self.client.get(reverse('client_search'), {'prenoms': 'Awa'})
        self.assertEqual(response.status_code, 200)

        clients = response.context['clients']
        self.assertEqual(clients.count(), 1)
        self.assertEqual(clients[0].noms, 'KONE')