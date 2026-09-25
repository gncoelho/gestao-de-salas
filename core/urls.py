from django.urls import path
from . import views

urlpatterns = [
    path('', views.sala_list, name='sala_list'),
    path('nova/', views.sala_create, name='sala_create'),
    path('<int:pk>/editar/', views.sala_update, name='sala_update'),
]
