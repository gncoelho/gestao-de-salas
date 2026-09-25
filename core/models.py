from django.conf import settings
from django.db import models

DIAS_SEMANA = [
    ("monday", "Segunda-feira"),
    ("tuesday", "Terça-feira"),
    ("wednesday", "Quarta-feira"),
    ("thursday", "Quinta-feira"),
    ("friday", "Sexta-feira"),
    ("saturday", "Sábado"),
    ("sunday", "Domingo"),
]


class Sala(models.Model):
    nome = models.CharField(max_length=100)
    horarios_disponiveis = models.JSONField(default=dict)

    def __str__(self):
        return self.nome

    @property
    def horarios_formatados(self):
        horarios = self.horarios_disponiveis or {}
        dias = []

        for codigo, nome in DIAS_SEMANA:
            slots = horarios.get(codigo) or []
            if not isinstance(slots, list):
                continue

            periodos = []
            for slot in slots:
                if not isinstance(slot, dict):
                    continue
                try:
                    inicio = int(slot["from"])
                    fim = int(slot["to"])
                except (KeyError, TypeError, ValueError):
                    continue
                periodos.append(f"{inicio:02d}:00 - {fim:02d}:00")

            if periodos:
                dias.append({"dia": nome, "periodos": periodos})

        return dias


class Agendamento(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="agendamentos"
    )
    sala = models.ForeignKey(
        Sala, on_delete=models.CASCADE, related_name="agendamentos"
    )
    data = models.DateField()
    hora_inicio = models.IntegerField()
    hora_fim = models.IntegerField()
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sala.nome} - {self.data} ({self.hora_inicio:02d}:00 - {self.hora_fim:02d}:00)"
