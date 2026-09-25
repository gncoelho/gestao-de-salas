from datetime import date
from io import StringIO
from unittest.mock import patch
from django.contrib.auth.models import User
from django.core.management import call_command, CommandError
from django.test import TestCase
from django.urls import reverse
from .models import Sala, Agendamento
from .views import calcular_proxima_data, encontrar_salas_disponiveis


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
            },
        )
        self.assertEqual(Sala.objects.count(), 1)
        self.assertEqual(sala.nome, "Sala Reunião A")
        self.assertEqual(sala.horarios_disponiveis["monday"], [{"from": 9, "to": 17}])
        self.assertEqual(str(sala), "Sala Reunião A")


class SalaViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )

    def test_sala_list_view_unauthenticated(self):
        response = self.client.get(reverse("sala_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_sala_create_view_unauthenticated(self):
        response = self.client.get(reverse("sala_create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_sala_update_view_unauthenticated(self):
        sala = Sala.objects.create(
            nome="Sala 101", horarios_disponiveis={"monday": [{"from": 9, "to": 17}]}
        )
        response = self.client.get(reverse("sala_update", args=[sala.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_sala_list_view_authenticated(self):
        self.client.login(username="testuser", password="password123")
        Sala.objects.create(
            nome="Sala 101", horarios_disponiveis={"monday": [{"from": 9, "to": 17}]}
        )
        response = self.client.get(reverse("sala_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sala 101")
        self.assertContains(response, "Segunda-feira")
        self.assertContains(response, "09:00 - 17:00")
        self.assertContains(response, "Editar")

    def test_sala_create_view_get(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(reverse("sala_create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Adicionar Nova Sala")

    def test_sala_create_view_post_valid(self):
        self.client.login(username="testuser", password="password123")
        data = {
            "nome": "Sala Inovação",
            "monday_from": 9,
            "monday_to": 17,
            "friday_from": 13,
            "friday_to": 18,
        }
        response = self.client.post(reverse("sala_create"), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("sala_list"))

        sala = Sala.objects.get(nome="Sala Inovação")
        self.assertEqual(
            sala.horarios_disponiveis,
            {
                "monday": [{"from": 9, "to": 17}],
                "friday": [{"from": 13, "to": 18}],
            },
        )

    def test_sala_create_view_post_invalid_hours(self):
        self.client.login(username="testuser", password="password123")
        data = {
            "nome": "Sala Inválida",
            "monday_from": 17,
            "monday_to": 9,  # 'from' > 'to'
        }
        response = self.client.post(reverse("sala_create"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "monday_to",
            "'monday' end hour ('to') must be greater than start hour ('from').",
        )
        self.assertEqual(Sala.objects.count(), 0)

    def test_sala_update_view_get(self):
        self.client.login(username="testuser", password="password123")
        sala = Sala.objects.create(
            nome="Sala 101", horarios_disponiveis={"monday": [{"from": 9, "to": 17}]}
        )
        response = self.client.get(reverse("sala_update", args=[sala.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Editar Sala")
        self.assertContains(response, "Sala 101")
        self.assertContains(response, 'value="9"')
        self.assertContains(response, 'value="17"')

    def test_sala_update_view_post_valid(self):
        self.client.login(username="testuser", password="password123")
        sala = Sala.objects.create(
            nome="Sala 101", horarios_disponiveis={"monday": [{"from": 9, "to": 17}]}
        )
        data = {
            "nome": "Sala 102",
            "tuesday_from": 10,
            "tuesday_to": 18,
        }
        response = self.client.post(reverse("sala_update", args=[sala.pk]), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("sala_list"))

        sala.refresh_from_db()
        self.assertEqual(sala.nome, "Sala 102")
        self.assertEqual(
            sala.horarios_disponiveis,
            {
                "tuesday": [{"from": 10, "to": 18}],
            },
        )


class CreateAdminCommandTest(TestCase):
    @patch.dict("os.environ", {"ENVIRONMENT": "development"}, clear=True)
    def test_create_admin_in_development(self):
        out = StringIO()
        call_command("create_admin", stdout=out)
        self.assertTrue(
            User.objects.filter(username="gui.admin", is_superuser=True).exists()
        )
        self.assertIn("Created admin user gui.admin", out.getvalue())

    @patch.dict("os.environ", {"ENVIRONMENT": "production"}, clear=True)
    def test_create_admin_in_production_fails(self):
        with self.assertRaises(CommandError):
            call_command("create_admin")
        self.assertFalse(User.objects.filter(username="gui.admin").exists())


class AgendamentoLogicTest(TestCase):
    def test_calcular_proxima_data(self):
        # Suppose base date is a Wednesday (2025-01-15)
        # Weekday map: monday=0, tuesday=1, wednesday=2, thursday=3, friday=4, saturday=5, sunday=6
        base = date(2025, 1, 15)  # Wednesday

        # Thursday (tomorrow): should be 2025-01-16
        self.assertEqual(
            calcular_proxima_data("thursday", base_date=base), date(2025, 1, 16)
        )

        # Wednesday (same day of week as base): must exclude today and return next Wednesday (2025-01-22)
        self.assertEqual(
            calcular_proxima_data("wednesday", base_date=base), date(2025, 1, 22)
        )

        # Tuesday (yesterday relative to base): should return next Tuesday (2025-01-21)
        self.assertEqual(
            calcular_proxima_data("tuesday", base_date=base), date(2025, 1, 21)
        )

    def test_encontrar_salas_disponiveis(self):
        sala1 = Sala.objects.create(
            nome="Sala Grande", horarios_disponiveis={"monday": [{"from": 8, "to": 12}]}
        )
        Sala.objects.create(
            nome="Sala Pequena",
            horarios_disponiveis={"monday": [{"from": 9, "to": 10}]},
        )

        target_date = date(2025, 1, 20)  # A Monday

        # Search 3 consecutive hours on Monday
        res = encontrar_salas_disponiveis("monday", 3, target_date)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["sala"], sala1)
        # Slots should be 8-11 and 9-12
        self.assertEqual(len(res[0]["slots"]), 2)

        # Now create booking in sala1 from 9 to 11
        user = User.objects.create_user(username="booker", password="pwd")
        Agendamento.objects.create(
            usuario=user, sala=sala1, data=target_date, hora_inicio=9, hora_fim=11
        )

        # Searching 3 consecutive hours now should find no room because 8-12 is broken into 8-9 and 11-12
        res2 = encontrar_salas_disponiveis("monday", 3, target_date)
        self.assertEqual(len(res2), 0)

        # Searching 1 hour should find sala1 (slots 8-9 and 11-12) and sala2 (slot 9-10)
        res3 = encontrar_salas_disponiveis("monday", 1, target_date)
        self.assertEqual(len(res3), 2)
        sala1_res = next(r for r in res3 if r["sala"] == sala1)
        slot_hours = [(s["hora_inicio"], s["hora_fim"]) for s in sala1_res["slots"]]
        self.assertIn((8, 9), slot_hours)
        self.assertIn((11, 12), slot_hours)


class AgendamentoViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )

    def test_agendar_sala_unauthenticated(self):
        response = self.client.get(reverse("agendar_sala"))
        self.assertEqual(response.status_code, 302)

    def test_agendar_sala_search_and_post(self):
        self.client.login(username="testuser", password="password123")
        sala = Sala.objects.create(
            nome="Sala Reunião",
            horarios_disponiveis={"monday": [{"from": 9, "to": 17}]},
        )

        # GET with search form
        response = self.client.get(
            reverse("agendar_sala"), {"horas_seguidas": 2, "dia_semana": "monday"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sala Reunião")
        self.assertContains(response, "09:00 - 11:00")

        # POST booking
        target_date = response.context["data_agendamento"]
        post_data = {
            "sala": sala.id,
            "data": target_date.strftime("%Y-%m-%d"),
            "hora_inicio": 9,
            "hora_fim": 11,
        }
        post_response = self.client.post(reverse("agendar_sala"), post_data)
        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(post_response, reverse("agendar_sala"))

        # Verify Agendamento object created
        self.assertEqual(Agendamento.objects.count(), 1)
        ag = Agendamento.objects.first()
        self.assertEqual(ag.usuario, self.user)
        self.assertEqual(ag.sala, sala)
        self.assertEqual(ag.data, target_date)
        self.assertEqual(ag.hora_inicio, 9)
        self.assertEqual(ag.hora_fim, 11)
