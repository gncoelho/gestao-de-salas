from django.test import TestCase
from django.urls import reverse

class WelcomeViewTests(TestCase):
    def test_welcome_page_status_code(self):
        response = self.client.get(reverse('core:welcome'))
        self.assertEqual(response.status_code, 200)

    def test_welcome_page_uses_correct_template(self):
        response = self.client.get(reverse('core:welcome'))
        self.assertTemplateUsed(response, 'core/welcome.html')

    def test_welcome_page_contains_bootstrap(self):
        response = self.client.get(reverse('core:welcome'))
        self.assertContains(response, 'bootstrap@5.3.3')
        self.assertContains(response, 'Bem-vindo ao seu projeto Django!')
