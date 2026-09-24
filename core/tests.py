import json
from django.test import TestCase
from django.urls import reverse
from .models import Sala


class SalaModelTest(TestCase):
    def test_create_sala(self):
        sala = Sala.objects.create(
            nome="Sala Reunião A",
            horarios_disponiveis={
                "monday": [{"from": 9, "to": 17}],
                "tuesday": [{"from": 10, "to": 18}],
                "wednesday": [],
                "thursday": [{"from": 8, "to": 12}, {"from": 14, "to": 18}],
                "friday": [{"from": 9, "to": 17}],
                "saturday": [],
                "sunday": [],
            }
        )
        self.assertEqual(Sala.objects.count(), 1)
        self.assertEqual(sala.nome, "Sala Reunião A")
        self.assertEqual(sala.horarios_disponiveis["monday"], [{"from": 9, "to": 17}])
        self.assertEqual(str(sala), "Sala Reunião A")


class SalaViewsTest(TestCase):
    def test_sala_list_view(self):
        Sala.objects.create(
            nome="Sala 101",
            horarios_disponiveis={"monday": [{"from": 9, "to": 17}]}
        )
        response = self.client.get(reverse('sala_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sala 101")
        self.assertContains(response, "monday")
        self.assertContains(response, "from")

    def test_sala_create_view_get(self):
        response = self.client.get(reverse('sala_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Adicionar Nova Sala")

    def test_sala_create_view_post_valid(self):
        data = {
            'nome': 'Sala Inovação',
            'monday_from': 9,
            'monday_to': 17,
            'friday_from': 13,
            'friday_to': 18,
        }
        response = self.client.post(reverse('sala_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('sala_list'))

        sala = Sala.objects.get(nome='Sala Inovação')
        self.assertEqual(sala.horarios_disponiveis, {
            'monday': [{'from': 9, 'to': 17}],
            'friday': [{'from': 13, 'to': 18}],
        })

    def test_sala_create_view_post_invalid_hours(self):
        data = {
            'nome': 'Sala Inválida',
            'monday_from': 17,
            'monday_to': 9,  # 'from' > 'to'
        }
        response = self.client.post(reverse('sala_create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'monday_to',
            "'monday' end hour ('to') must be greater than start hour ('from')."
        )
        self.assertEqual(Sala.objects.count(), 0)
