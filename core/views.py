from datetime import date, timedelta
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from .models import Sala, Agendamento
from .forms import SalaForm, AgendamentoSearchForm, AgendamentoForm

WEEKDAY_MAP = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def calcular_proxima_data(dia_semana_str, base_date=None):
    if base_date is None:
        base_date = date.today()

    target_weekday = WEEKDAY_MAP[dia_semana_str]
    # The search starts from tomorrow (today + 1 day)
    current = base_date + timedelta(days=1)
    while current.weekday() != target_weekday:
        current += timedelta(days=1)
    return current


def encontrar_salas_disponiveis(dia_semana_str, horas_seguidas, data_agendamento):
    salas_com_horarios = []
    salas = Sala.objects.all()

    for sala in salas:
        horarios = sala.horarios_disponiveis or {}
        slots = horarios.get(dia_semana_str, [])
        if not isinstance(slots, list):
            continue

        # Get existing bookings for this room on this date
        agendamentos_existentes = Agendamento.objects.filter(
            sala=sala, data=data_agendamento
        )

        slots_disponiveis = []
        for slot in slots:
            if not isinstance(slot, dict):
                continue
            try:
                slot_start = int(slot["from"])
                slot_end = int(slot["to"])
            except (KeyError, TypeError, ValueError):
                continue

            # Slide a window of `horas_seguidas` within [slot_start, slot_end]
            for start_hour in range(slot_start, slot_end - horas_seguidas + 1):
                end_hour = start_hour + horas_seguidas

                # Check if this sub-slot overlaps with any existing booking
                colide = False
                for ag in agendamentos_existentes:
                    if max(start_hour, ag.hora_inicio) < min(end_hour, ag.hora_fim):
                        colide = True
                        break

                if not colide:
                    slots_disponiveis.append(
                        {
                            "hora_inicio": start_hour,
                            "hora_fim": end_hour,
                            "formatado": f"{start_hour:02d}:00 - {end_hour:02d}:00",
                        }
                    )

        if slots_disponiveis:
            salas_com_horarios.append(
                {
                    "sala": sala,
                    "slots": slots_disponiveis,
                }
            )

    return salas_com_horarios


def agendar_sala(request):
    form = AgendamentoSearchForm(request.GET or None)
    salas_encontradas = None
    data_agendamento = None

    if request.method == "POST":
        booking_form = AgendamentoForm(request.POST)
        if booking_form.is_valid():
            agendamento = booking_form.save(commit=False)
            agendamento.usuario = request.user
            agendamento.save()
            messages.success(request, "Agendamento realizado com sucesso!")
            return redirect("agendar_sala")
        else:
            messages.error(request, "Erro ao realizar agendamento. Verifique os dados.")

    if form.is_valid():
        horas_seguidas = form.cleaned_data["horas_seguidas"]
        dia_semana = form.cleaned_data["dia_semana"]
        data_agendamento = calcular_proxima_data(dia_semana)
        salas_encontradas = encontrar_salas_disponiveis(
            dia_semana, horas_seguidas, data_agendamento
        )

    context = {
        "form": form,
        "salas_encontradas": salas_encontradas,
        "data_agendamento": data_agendamento,
        "meus_agendamentos": Agendamento.objects.filter(usuario=request.user).order_by(
            "data", "hora_inicio"
        ),
    }
    return render(request, "core/agendamento.html", context)


def sala_list(request):
    salas = Sala.objects.all()
    return render(request, "core/sala_list.html", {"salas": salas})


def sala_create(request):
    if request.method == "POST":
        form = SalaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("sala_list")
    else:
        form = SalaForm()
    return render(request, "core/sala_form.html", {"form": form})


def sala_update(request, pk):
    sala = get_object_or_404(Sala, pk=pk)
    if request.method == "POST":
        form = SalaForm(request.POST, instance=sala)
        if form.is_valid():
            form.save()
            return redirect("sala_list")
    else:
        form = SalaForm(instance=sala)
    return render(request, "core/sala_form.html", {"form": form, "sala": sala})
