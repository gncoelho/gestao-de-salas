from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.welcome, name="welcome"),
    path("login/", LoginView.as_view(template_name="webapp/login.html"), name="login"),
    path("logout/", login_not_required(LogoutView.as_view()), name="logout"),
    path("cadastro/", views.cadastro, name="cadastro"),
]
