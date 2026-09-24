from django.db import models

DIAS_SEMANA = [
    ('monday', 'Segunda-feira'),
    ('tuesday', 'Terça-feira'),
    ('wednesday', 'Quarta-feira'),
    ('thursday', 'Quinta-feira'),
    ('friday', 'Sexta-feira'),
    ('saturday', 'Sábado'),
    ('sunday', 'Domingo'),
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
                    inicio = int(slot['from'])
                    fim = int(slot['to'])
                except (KeyError, TypeError, ValueError):
                    continue
                periodos.append(f'{inicio:02d}:00 - {fim:02d}:00')

            if periodos:
                dias.append({'dia': nome, 'periodos': periodos})

        return dias
