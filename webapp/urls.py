from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('login/', LoginView.as_view(template_name='webapp/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('cadastro/', views.cadastro, name='cadastro'),
]
