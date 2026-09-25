from django.shortcuts import get_object_or_404, render, redirect
from .models import Sala
from .forms import SalaForm

def sala_list(request):
    salas = Sala.objects.all()
    return render(request, 'core/sala_list.html', {'salas': salas})

def sala_create(request):
    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sala_list')
    else:
        form = SalaForm()
    return render(request, 'core/sala_form.html', {'form': form})

def sala_update(request, pk):
    sala = get_object_or_404(Sala, pk=pk)
    if request.method == 'POST':
        form = SalaForm(request.POST, instance=sala)
        if form.is_valid():
            form.save()
            return redirect('sala_list')
    else:
        form = SalaForm(instance=sala)
    return render(request, 'core/sala_form.html', {'form': form, 'sala': sala})
