"""
@testops-description
Valida autenticação tradicional do Django no webapp: redirecionamento da home
sem sessão, cadastro com usuário e senha, login, e logout por POST.
"""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AutenticacaoTests(TestCase):
    def test_home_redireciona_visitante_para_login(self):
        resposta = self.client.get(reverse('welcome'))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse('login'), resposta.url)

    def test_cadastro_cria_usuario_e_entra(self):
        resposta = self.client.post(
            reverse('cadastro'),
            {
                'username': 'sala_admin',
                'password1': 'SenhaForte123',
                'password2': 'SenhaForte123',
            },
        )
        self.assertRedirects(resposta, reverse('welcome'))
        self.assertTrue(User.objects.filter(username='sala_admin').exists())

    def test_login_com_usuario_e_senha(self):
        User.objects.create_user(username='operador', password='SenhaForte123')
        resposta = self.client.post(
            reverse('login'),
            {'username': 'operador', 'password': 'SenhaForte123'},
        )
        self.assertRedirects(resposta, reverse('welcome'))

    def test_logout_encerra_sessao(self):
        User.objects.create_user(username='operador', password='SenhaForte123')
        self.client.login(username='operador', password='SenhaForte123')
        resposta = self.client.post(reverse('logout'))
        self.assertRedirects(resposta, reverse('login'))
        home = self.client.get(reverse('welcome'))
        self.assertEqual(home.status_code, 302)
