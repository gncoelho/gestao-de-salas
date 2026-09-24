from django.urls import path
from . import views

urlpatterns = [
    path('', views.sala_list, name='sala_list'),
    path('salas/nova/', views.sala_create, name='sala_create'),
]
