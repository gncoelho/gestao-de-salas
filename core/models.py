from django.db import models


class Sala(models.Model):
    nome = models.CharField(max_length=100)
    horarios_disponiveis = models.JSONField(default=dict)

    def __str__(self):
        return self.nome
